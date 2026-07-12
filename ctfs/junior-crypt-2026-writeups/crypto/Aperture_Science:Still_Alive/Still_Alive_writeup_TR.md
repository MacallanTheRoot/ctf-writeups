# Junior Crypt 2026 CTF - `Aperture Science: Still Alive` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Crypto  
**Challenge dosyaları:** `public.pem`, `ciphertexts.json`  
**Flag formatı:** `grodno{...}`

---

## Challenge Açıklaması

Author: @vvanuss
medium

A restricted Aperture Science record associated with GLaDOS was recovered from an internal storage segment that survived the shutdown of the facility.

The surviving materials are incomplete, but they are sufficient to reconstruct what was meant to remain hidden.

Recover the original message.

Flag format: grodno{}
---

## Özet

Public exponent `e = 3`. Ciphertext'ler ilişkili iki plaintext'e ait:

```text
c1 = m^3 mod n
c2 = (a*m + b)^3 mod n
```

Bu yapı Franklin-Reiter related-message saldırısına uygundur. `Z_n[x]` üzerinde polynomial GCD alarak ortak kök olan `m` geri çıkarılır.

---

## 1. RSA Parametreleri

Public key içinde exponent şu şekilde görünüyor:

```text
Exponent: 3
```

JSON dosyasında ise:

```text
c1, c2, a, b
```

İlişki:

```text
m2 = a*m + b
```

Bu yüzden iki polinom kurabiliriz:

```text
f(x) = x^3 - c1
g(x) = (a*x + b)^3 - c2
```

İki polinom da modulo `n` altında aynı `m` köküne sahiptir.

---

## 2. Franklin-Reiter Saldırısı

`f(x)` ve `g(x)` polinomlarının RSA modülü üzerinde GCD'si alınır. Sonuç birinci dereceden polinomdur:

```text
x - m
```

Bulunan integer daha sonra byte dizisine çevrilir.

---

## 3. Solver

Tekrar üretilebilir solver [`solver.py`](./solver.py) içinde:

```bash
python3 solver.py
```

Beklenen çıktı:

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

Aynı modulus altında düşük exponent RSA ile lineer ilişkili iki mesaj şifrelenmiş. `e = 3` olduğunda bu ilişki, `n` faktörlenmeden orijinal mesajı geri almak için yeterlidir.
