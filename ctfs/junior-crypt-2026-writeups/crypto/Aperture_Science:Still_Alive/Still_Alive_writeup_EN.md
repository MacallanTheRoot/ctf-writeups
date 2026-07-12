# Junior Crypt 2026 CTF - `Aperture Science: Still Alive` Writeup

- **Writeup Author:** Efe Sahinbas
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Crypto  
**Challenge files:** `public.pem`, `ciphertexts.json`  
**Flag format:** `grodno{...}`

---

## Challenge Description

Author: @vvanuss
medium

A restricted Aperture Science record associated with GLaDOS was recovered from an internal storage segment that survived the shutdown of the facility.

The surviving materials are incomplete, but they are sufficient to reconstruct what was meant to remain hidden.

Recover the original message.

Flag format: grodno{}

---

## Summary

The public exponent is `e = 3`. The ciphertexts correspond to related plaintexts:

```text
c1 = m^3 mod n
c2 = (a*m + b)^3 mod n
```

This is a Franklin-Reiter related-message attack. Computing the polynomial GCD over `Z_n[x]` recovers the shared root `m`.

---

## 1. RSA Parameters

The public key shows:

```text
Exponent: 3
```

The JSON file contains:

```text
c1, c2, a, b
```

The relation is:

```text
m2 = a*m + b
```

So we can build two polynomials:

```text
f(x) = x^3 - c1
g(x) = (a*x + b)^3 - c2
```

Both polynomials have the same root `m` modulo `n`.

---

## 2. Franklin-Reiter Attack

Taking the GCD of `f(x)` and `g(x)` over the RSA modulus gives a degree-one polynomial:

```text
x - m
```

The recovered integer is then converted back to bytes.

---

## 3. Solver

The reproducible solver is included as [`solver.py`](./solver.py):

```bash
python3 solver.py
```

Expected output:

```text
grodno{571ll_4l1v3_bu7_g14d05_k3375_r3w5171ng_m35s4g35}
```

---

## 4. Flag

```text
grodno{571ll_4l1v3_bu7_g14d05_k3375_r3w5171ng_m35s4g35}
```

---

## Root Cause

Low-exponent RSA was used to encrypt two linearly related messages under the same modulus. With `e = 3`, the relation is enough to recover the original message without factoring `n`.
