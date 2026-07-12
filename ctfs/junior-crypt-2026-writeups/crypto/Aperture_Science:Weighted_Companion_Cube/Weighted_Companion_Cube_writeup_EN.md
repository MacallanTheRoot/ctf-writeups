# Junior Crypt 2026 CTF - `Weighted Companion Cube` Writeup

- **Writeup Author:** Efe Sahinbas
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Crypto  
**Challenge files:** `metadata.json`, `catalog.json`, `known_archives.json`, `secret_archive.hex`  
**Flag format:** `grodno{...}`

---

## Challenge Description

A sealed Aperture Science archive related to Companion Cube logistics was recovered. Most records looked routine, but one protected entry had to be recovered.

The files describe a fixed-width archive format:

```text
[Aperture Archive]
item=18
status=12
sector=12
memo=64
```

The metadata also states that every archive was encrypted under the same boot state.

---

## Summary

The archive uses a stream-like encryption mode with keystream reuse. A known plaintext record can be reconstructed from the catalog and XORed with its ciphertext to recover the keystream. The same keystream decrypts `secret_archive.hex`.

---

## 1. Reconstructing the Record Format

Each record is 153 bytes long and uses fixed-width padded fields:

```python
def record(item, status, sector, memo):
    return (
        "[Aperture Archive]\n"
        f"item={item:<18}\n"
        f"status={status:<12}\n"
        f"sector={sector:<12}\n"
        f"memo={memo:<64}\n"
    ).encode()
```

The first known ciphertext decrypts cleanly when the plaintext is:

```text
item=companion cube
status=issued
sector=alpha-17
memo=incineration queue delayed until morale stabilizes
```

---

## 2. Keystream Reuse

For a stream cipher:

```text
ciphertext = plaintext XOR keystream
```

So the keystream can be recovered with:

```text
keystream = known_plaintext XOR known_ciphertext
```

Then the protected archive is decrypted with:

```text
secret_plaintext = secret_ciphertext XOR keystream
```

---

## 3. Solver

The reproducible solver is included as [`solver.py`](./solver.py):

```bash
python3 solver.py
```

Expected output:

```text
[Aperture Archive]
item=cake voucher
status=issued
sector=omega-01
memo=grodno{c0mp4n10n_cub3_7h15_15_57r1c7ly_4_m4ny_71m3_p4d}
```

---

## 4. Flag

```text
grodno{c0mp4n10n_cub3_7h15_15_57r1c7ly_4_m4ny_71m3_p4d}
```

---

## Root Cause

The same stream keystream was reused for multiple fixed-format records. Because one record could be reconstructed, the keystream was exposed and reused to decrypt the protected record.
