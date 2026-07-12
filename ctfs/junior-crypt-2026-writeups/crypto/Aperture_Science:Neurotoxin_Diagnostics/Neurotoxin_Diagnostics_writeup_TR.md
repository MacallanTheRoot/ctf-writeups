# Junior Crypt 2026 CTF - `Neurotoxin Diagnostics` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Crypto  
**Zorluk:** Hard  
**Challenge dosyaları:** `metadata.json`, `packet.hex`, `timing_trace.json`  
**Flag formatı:** `grodno{...}`

---

## Challenge Açıklaması

Challenge bize bir AES-CBC packet ve diagnostic run sırasında alınmış timing telemetry veriyor. Elimizde yalnızca timing verisi olduğu için plaintext'i side-channel üzerinden yeniden kurmamız gerekiyor.

---

## Özet

Timing trace, padding-oracle denemelerini içeriyor. Her `(block, pad, guess)` grubu için doğru guess'in ortalama çalışma süresi belirgin şekilde daha yüksek. Her byte için en yavaş guess seçildiğinde padding-oracle intermediate değeri elde ediliyor. Bu değer önceki CBC bloğu ve padding byte'ı ile XOR'lanınca plaintext çıkıyor.

---

## 1. Packet Yapısı

`packet.hex` 16 byte'lık bir marker ile başlıyor:

```text
NEUROTOXIN_TEST!
```

Geri kalan veri AES-CBC ciphertext. Packet 16 byte bloklara ayrıldığında ilk blok IV benzeri önceki blok, devamındaki bloklar ise şifreli bloklar olarak kullanılıyor.

---

## 2. Timing Trace

Her timing satırı şu alanlara sahip:

```json
{
  "block": 4,
  "pad": 4,
  "guess": 190,
  "trial": 0,
  "elapsed_ns": 1275767
}
```

Her block ve padding değeri için 256 guess üçer kez denenmiş. Doğru guess sürekli olarak yaklaşık 2.5-2.7 ms civarında görünüyor; diğer denemeler ise daha düşük gürültü bandında kalıyor.

---

## 3. Plaintext Byte'larını Çıkarmak

CBC padding oracle için byte hesabı:

```text
plaintext_byte = guess XOR previous_ciphertext_byte XOR pad
```

Script timing satırlarını `(block, pad, guess)` bazında gruplayıp ortalama süreyi alıyor, en yavaş guess'i seçiyor ve byte'ları sağdan sola yeniden kuruyor.

Elde edilen plaintext:

```text
diag=neurotoxin;status=stable;subject=chell;memo=grodno{n3ur070x1n_d14gn0571c5_l34k_7hr0ugh_71m1ng_4l0n3};closing=still_alive
```

---

## 4. Solver

Tekrar üretilebilir solver [`solver.py`](./solver.py) içinde:

```bash
python3 solver.py
```

Beklenen çıktı:

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

Sistem padding-oracle davranışını timing üzerinden sızdırıyor. AES key bilinmese bile bu timing side-channel, CBC plaintext byte'larını tek tek geri almak için yeterli oluyor.
