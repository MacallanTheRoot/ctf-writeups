# Junior Crypt 2026 CTF - `Stream Calibration` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Crypto  
**Challenge dosyaları:** `encoder.py`, `ciphertext.txt`  
**Flag formatı:** `grodno{...}`

---

## Challenge Açıklaması

Challenge bize bir calibration subsystem encoder'ı ve tek bir ciphertext veriyor. Amaç, şifrelenmiş Aperture Science diagnostic mesajını geri almak.

---

## Özet

Encoder 32-bit linear congruential generator kullanıyor, fakat seed yalnızca 20 bite düşürülüyor:

```python
state = seed & 0xFFFFF
```

Bu da sadece `2^20` olası başlangıç durumu bırakıyor. Bu yüzden ciphertext doğrudan brute force ile çözülebiliyor.

---

## 1. Keystream'i İncelemek

Keystream üreteci şu şekilde:

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

`facility_seed` integer olarak verilse de yalnızca düşük 20 biti kullanılıyor. Bu nedenle gerçek keyspace brute force için oldukça küçük.

---

## 2. Brute Force

Her seed için:

```text
plaintext = ciphertext XOR keystream(seed, len(ciphertext))
```

Doğru plaintext, beklenen `grodno{` flag marker'ı ile bulunuyor.

---

## 3. Solver

Tekrar üretilebilir solver [`solver.py`](./solver.py) içinde:

```bash
python3 solver.py
```

Beklenen çıktı:

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

Stream cipher seed'i kullanılmadan önce 20 bite indiriliyor. Bu da keystream'in exhaustive search ile bulunmasına yol açıyor.
