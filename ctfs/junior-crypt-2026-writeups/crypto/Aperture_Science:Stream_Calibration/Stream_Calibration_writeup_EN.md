# Junior Crypt 2026 CTF - `Stream Calibration` Writeup

- **Writeup Author:** Efe Sahinbas
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Crypto  
**Challenge files:** `encoder.py`, `ciphertext.txt`  
**Flag format:** `grodno{...}`

---

## Challenge Description

The challenge provides a calibration subsystem encoder and one ciphertext. The goal is to recover the encrypted Aperture Science diagnostic message.

---

## Summary

The encoder uses a 32-bit linear congruential generator, but the seed is truncated to only 20 bits:

```python
state = seed & 0xFFFFF
```

That leaves only `2^20` possible starting states, so the ciphertext can be brute-forced directly.

---

## 1. Inspecting the Keystream

The keystream generator is:

```python
MOD = 1 << 32
A = 1664525
C = 1013904223

def keystream(seed, length):
    state = seed & 0xFFFFF
    out = bytearray()
    for _ in range(length):
        state = (A * state + C) % MOD
        out.append((state >> 24) & 0xFF)
    return bytes(out)
```

Although `facility_seed` is passed as an integer, only the low 20 bits are used. This makes the actual key space small enough to exhaust.

---

## 2. Brute Force

For each possible seed:

```text
plaintext = ciphertext XOR keystream(seed, len(ciphertext))
```

The correct plaintext is detected by the expected flag marker `grodno{`.

---

## 3. Solver

The reproducible solver is included as [`solver.py`](./solver.py):

```bash
python3 solver.py
```

Expected output:

```text
seed: 369020
[Aperture Science Internal]
classification=stable
speaker=GLaDOS
memo=grodno{7h15_w45_4_7r1umph_bu7_7h3_533d_w45_700_5m4ll}
```

---

## 4. Flag

```text
grodno{7h15_w45_4_7r1umph_bu7_7h3_533d_w45_700_5m4ll}
```

---

## Root Cause

The stream cipher seed is reduced to 20 bits before use. This makes the keystream predictable by exhaustive search.
