# Junior Crypt 2026 CTF - `Neurotoxin Diagnostics` Writeup

- **Writeup Author:** Efe Sahinbas
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Crypto  
**Difficulty:** Hard  
**Challenge files:** `metadata.json`, `packet.hex`, `timing_trace.json`  
**Flag format:** `grodno{...}`

---

## Challenge Description

The challenge provides an AES-CBC packet and timing telemetry from a diagnostic run. Only the packet timing data survived, so the plaintext has to be reconstructed from the side channel.

---

## Summary

The timing trace records padding-oracle trials. For each `(block, pad, guess)` tuple, the correct guess has a noticeably higher average runtime. Selecting the slowest guess for every byte gives the padding-oracle intermediate value. XORing it with the previous CBC block and the target padding byte recovers the plaintext.

---

## 1. Packet Layout

`packet.hex` starts with a 16-byte marker:

```text
NEUROTOXIN_TEST!
```

The rest is AES-CBC ciphertext. Splitting the packet into 16-byte blocks gives one IV-like block followed by encrypted blocks.

---

## 2. Timing Trace

Each timing row has:

```json
{
  "block": 4,
  "pad": 4,
  "guess": 190,
  "trial": 0,
  "elapsed_ns": 1275767
}
```

For every block and padding value, all 256 guesses were tried three times. The correct guess consistently appears around 2.5-2.7 ms, while the noise band is much lower.

---

## 3. Recovering Plaintext Bytes

For a CBC padding oracle byte:

```text
plaintext_byte = guess XOR previous_ciphertext_byte XOR pad
```

The script groups timing entries by `(block, pad, guess)`, takes the mean runtime, selects the slowest guess, and reconstructs all bytes from right to left.

The recovered plaintext is:

```text
diag=neurotoxin;status=stable;subject=chell;memo=grodno{n3ur070x1n_d14gn0571c5_l34k_7hr0ugh_71m1ng_4l0n3};closing=still_alive
```

---

## 4. Solver

The reproducible solver is included as [`solver.py`](./solver.py):

```bash
python3 solver.py
```

Expected output:

```text
diag=neurotoxin;status=stable;subject=chell;memo=grodno{n3ur070x1n_d14gn0571c5_l34k_7hr0ugh_71m1ng_4l0n3};closing=still_alive
```

---

## 5. Flag

```text
grodno{n3ur070x1n_d14gn0571c5_l34k_7hr0ugh_71m1ng_4l0n3}
```

---

## Root Cause

The system leaked padding-oracle behavior through timing. Even without the AES key, the timing side channel exposed enough information to recover each CBC plaintext byte.
