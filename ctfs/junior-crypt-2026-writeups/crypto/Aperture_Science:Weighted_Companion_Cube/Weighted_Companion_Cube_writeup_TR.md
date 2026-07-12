# Junior Crypt 2026 CTF - `Weighted Companion Cube` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Crypto  
**Challenge dosyaları:** `metadata.json`, `catalog.json`, `known_archives.json`, `secret_archive.hex`  
**Flag formatı:** `grodno{...}`

---

## Challenge Açıklaması

Companion Cube lojistiğiyle ilişkili kapalı bir Aperture Science arşivi verilmişti. Kayıtların çoğu normal görünüyordu, fakat korumalı bir kaydın içeriğini çıkarmamız gerekiyordu.

Dosyalar sabit uzunluklu bir arşiv formatı tarif ediyordu:

```text
[Aperture Archive]
item=18
status=12
sector=12
memo=64
```

Metadata içindeki önemli not ise bütün arşivlerin aynı boot-state altında şifrelendiğini söylüyordu.

---

## Özet

Şifreleme stream-cipher gibi davranıyor ve aynı keystream tekrar kullanılıyor. Catalog üzerinden bilinen bir plaintext kaydı yeniden oluşturup ciphertext ile XOR'layarak keystream'i elde edebiliyoruz. Aynı keystream `secret_archive.hex` dosyasını çözmek için yeterli oluyor.

---

## 1. Kayıt Formatını Yeniden Kurmak

Her kayıt 153 byte uzunluğunda ve alanlar boşlukla pad ediliyor:

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

İlk bilinen ciphertext şu plaintext ile temiz şekilde eşleşiyor:

```text
item=companion cube
status=issued
sector=alpha-17
memo=incineration queue delayed until morale stabilizes
```

---

## 2. Keystream Tekrarı

Stream cipher mantığında:

```text
ciphertext = plaintext XOR keystream
```

Bu yüzden keystream şu şekilde çıkarılır:

```text
keystream = known_plaintext XOR known_ciphertext
```

Ardından korumalı kayıt çözülür:

```text
secret_plaintext = secret_ciphertext XOR keystream
```

---

## 3. Solver

Tekrar üretilebilir solver [`solver.py`](./solver.py) içinde:

```bash
python3 solver.py
```

Beklenen çıktı:

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

Aynı stream keystream birden fazla sabit formatlı kayıt için tekrar kullanılmış. Bir kaydın plaintext'i yeniden oluşturulabildiği için keystream açığa çıkıyor ve korumalı kayıt da aynı keystream ile çözülebiliyor.
