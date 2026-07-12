# Junior Crypt 2026 CTF - `WrongKube++` Writeup

- **Writeup Author:** Efe Şahinbaş
- **Challenge Author:** @vvanuss
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Reverse Engineering  
**Difficulty:** Hard  
**File:** `WrongKube++.exe`  
**SHA-256:** `9eb1d7cd74bdc195df16ab0bdca9a55c2df7d33e0b624c8fa9f38e1bf5ef7509`

---

## Summary

`WrongKube++.exe` is a 64-bit PyInstaller application with a PyQt6 interface. Its Python layer normalizes a Kubernetes-like project and passes it to the bundled `wrongkube_validator.dll`. The flag is not present in the Python bytecode; it is encrypted inside the native validator's success branch.

Final flag:

```text
grodno{wr0ngkub3pp_5p3ctr4l_qu0rum_0v3rdr1v3}
```

## 1. Initial Triage

```bash
file 'WrongKube++.exe'
strings -a -el 'WrongKube++.exe'
```

The 36 MB PE32+ GUI executable contains PyInstaller loader messages, `python312.dll`, PyQt6, and several custom entries:

```text
main
src.ui
src.validator_bridge
assets\demo.wkubeproj
build\wrongkube_validator.dll
PYZ.pyz
```

## 2. Extracting PyInstaller

The archive can be inspected with PyInstaller's own viewer:

```bash
pyi-archive_viewer -r -b 'WrongKube++.exe'
```

Extracting `src.validator_bridge`, the demo project, and the validator DLL reveals the native API contract:

```python
lib.validate_cluster.argtypes = [ctypes.c_char_p]
lib.validate_cluster.restype = ctypes.c_void_p
```

The bridge serializes nodes and edges into deterministic JSON. The native function returns JSON containing `ok`, `score`, `signature`, `summary`, and `flag`.

## 3. Native Validator

The DLL exports `validate_cluster` and `free_result`. The success path requires:

```asm
cmp r10d, 0x2911e
jne failure
```

After this check, 45 encrypted bytes at virtual address `0x18002b310` are decoded in two-byte rounds using an LCG/XOR stream. The initial state is:

```text
seed    = 0xc5b1d2ff
state_a = 0x47502943
state_b = 0x47502932
state_c = 0x3c6ef35f
```

The first byte of each pair follows the equivalent operation:

```python
stream = seed * 0x19660d + state_c
plain = encrypted ^ (stream >> 16) ^ stream ^ step
```

The second byte uses a separate state update. The included `solve.py` reproduces the full assembly loop directly.

## 4. Solution

After extracting the DLL, run:

```bash
python3 solve.py wrongkube_validator.dll
```

Output:

```text
grodno{wr0ngkub3pp_5p3ctr4l_qu0rum_0v3rdr1v3}
```

## Flag

```text
grodno{wr0ngkub3pp_5p3ctr4l_qu0rum_0v3rdr1v3}
```

## Key Point

The GUI and cluster constraints are distractions. The native success branch contains a deterministic decryptor, so the encrypted flag can be recovered without reconstructing the accepted topology.
