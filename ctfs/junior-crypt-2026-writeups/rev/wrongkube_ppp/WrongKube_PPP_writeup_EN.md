# Junior Crypt 2026 CTF - `WrongKube+++` Writeup

- **Author:** @vvanuss
- **Category:** Reverse Engineering
- **Difficulty:** Nightmare+
- **File:** `WrongKube+++.exe`
- **SHA-256:** `ac8addb97b5cf22b73442c864d7ab6c8f6ad8c0c0aa8ed94edfdea23b9f200f4`

## Summary

`WrongKube+++.exe` is a 64-bit PyInstaller application with a PyQt6 interface. The Python layer serializes a Kubernetes-like project and sends it to a native DLL named `wrongkube_validator.dll`. The bundled demo project is intentionally close to the accepted topology.

Instead of reversing every validator stage, I extracted the DLL and demo project, called the exported validator directly, and used its detailed score fields as an oracle. Four corrections turned the demo into the canonical topology and made the DLL return the flag.

## 1. Initial Triage

```bash
file 'WrongKube+++.exe'
rabin2 -I 'WrongKube+++.exe'
rabin2 -S 'WrongKube+++.exe'
```

The executable is a PE32+ GUI application with a very large overlay. Strings near the end identify the bundle as PyInstaller and reveal the relevant files:

```text
assets\demo.wkubeproj
build\wrongkube_validator.dll
base_library.zip
PYZ.pyz
python312.dll
```

The native DLL exports two useful functions:

```text
validate_cluster
free_result
```

Its result format is also visible in the strings:

```json
{"ok":false,"score":0,"signature":0,"summary":"...","flag":"",...}
```

## 2. Extracting the PyInstaller Bundle

PyInstaller's own reader can extract the files without running the GUI:

```python
from PyInstaller.archive.readers import CArchiveReader

archive = CArchiveReader("WrongKube+++.exe")
for name in (
    "assets\\demo.wkubeproj",
    "build\\wrongkube_validator.dll",
    "PYZ.pyz",
):
    with open(name.replace("\\", "_"), "wb") as output:
        output.write(archive.extract(name))
```

The `PYZ.pyz` archive contains `src.validator_bridge`. Disassembling that Python 3.12 bytecode shows the exact JSON contract used by the DLL.

Each node is flattened to:

```text
id, type, name, namespace, labels, selector, replicas, port, mount
```

Each edge is flattened to:

```text
source_id, target_id, binding, role, port
```

## 3. Calling the Native Validator

The included [`call_validator.c`](./call_validator.c) helper loads the Windows DLL and prints its JSON response. It can be cross-compiled on Linux:

```bash
x86_64-w64-mingw32-gcc -O2 \
  -o call_validator.exe call_validator.c
```

I ran the helper in Wine. The untouched, correctly serialized demo returned:

```json
{
  "ok": false,
  "score": 150,
  "signature": 811730,
  "summary": "Control plane is close. Northbound, audit, specter, and oracle lanes still disagree.",
  "flag": "",
  "manifest": 28,
  "edges": 60,
  "meta": 23,
  "shadow": 15,
  "specter": 13,
  "phantom": 11
}
```

This was much more useful than the GUI because every mutation could be measured immediately.

## 4. Finding the Broken Resources

Deleting each node once and comparing the `manifest` counter identified the three nodes that did not contribute to the initial score:

```text
dep-specter
svc-specter
pod-veil
```

Their inconsistencies were visible in the project data:

1. `specter-daemon` belonged to `audit-lane`, although the specter resources and containment edge placed it in `specter-net`.
2. `specter-svc` used port `9444`, while its route and expose edges used `9555`.
3. `veil-1` claimed the `specter-map` mount, but the final topology expected the specter secret.

The corrected node properties are:

```text
dep-specter.namespace = specter-net
svc-specter.port      = 9555
pod-veil.mount        = specter-key
```

After those changes the validator reached `manifest=31`, but the oracle stage still failed. The last missing relationship was a mount edge:

```text
sec-specter -> pod-veil
binding = mount
role    = specter-key
port    = 0
```

The included [`solve.py`](./solve.py) applies all four changes to the extracted project and produces the flattened validator payload.

## 5. Accepted Result

With the corrected payload, the validator returned:

```json
{
  "ok": true,
  "score": 158,
  "signature": 890544,
  "summary": "Abyssal control plane reconciled. Sextuple witness accepted.",
  "manifest": 31,
  "edges": 61,
  "meta": 24,
  "shadow": 16,
  "specter": 14,
  "phantom": 12,
  "vm": 9,
  "vm2": 8,
  "vm3": 7,
  "vm4": 6,
  "vm5": 8,
  "vm6": 7
}
```

## Flag

```text
grodno{wr0ngkub3ppp_4by55_0r4cl3_qu0rum_3xtr3m3}
```

## Root Cause

The challenge is a constraint-recovery problem hidden behind a GUI and several derived validator layers. The important shortcut is that the native validator exposes fine-grained counters and summaries, turning it into an oracle for locating malformed nodes and relationships.
