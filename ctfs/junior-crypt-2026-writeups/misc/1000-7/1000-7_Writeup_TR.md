# Junior Crypt 2026 CTF - `1000-7` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Misc / MIDI Steganography  
**Challenge dosyası:** `chal.mid`  
**Zorluk:** Medium  
**Flag formatı:** `grodno{...}`

---

## Challenge Açıklaması

> Some melodies stay in your head.  
> Some leave something else behind.

Challenge bir MIDI dosyası veriyor. İpucundaki “leave something else behind” ifadesi, duyulan notalardan çok MIDI olayları içinde bırakılan ek veriye bakmamız gerektiğini söylüyor.

## 1. Dosya Yapısı

```bash
file chal.mid
```

Dosya, iki track içeren geçerli bir Standard MIDI format 1 dosyasıdır. İlk track'in adı `Unravel - Tokyo Ghoul` olarak görünür. Nota olaylarının kendisi normal bir müzik parçası oluşturduğu için nota dışındaki MIDI olaylarını incelemek gerekir.

## 2. Pitch-bend Olaylarındaki Anormallik

İkinci track ayrıştırıldığında toplam 752 pitch-bend olayı bulunur. Bu olayların üst veri baytı yalnızca iki değer alır:

```text
82, 46, 46, 82, 82, 46, ...
```

Olayları ikili gruplara ayırınca yalnızca `(82, 46)` ve `(46, 82)` çiftleri görülür. İki değerin sırası bilgi taşımaktadır:

```text
(82, 46) -> 1
(46, 82) -> 0
```

752 olay, 376 çift ve dolayısıyla 376 bit üretir. Bitleri sekizerli gruplara ayırıp MSB-first biçiminde baytlara dönüştürdüğümüzde şu veri çıkar:

```python
b'\xc0\xde*grodno{U1tr@_m3g@_5up3r_Gul_M1d_SF_1000-7}\xc5\x11'
```

Baştaki ve sondaki baytlar dolgu/gürültüdür; aradaki flag açıkça okunur.

## 3. Otomatik Çözüm

Depodaki solver yalnızca Python standart kütüphanesini kullanır:

```bash
python3 solver.py chal.mid
```

Çıktı:

```text
grodno{U1tr@_m3g@_5up3r_Gul_M1d_SF_1000-7}
```

## Flag

```text
grodno{U1tr@_m3g@_5up3r_Gul_M1d_SF_1000-7}
```

## Root Cause

Flag, MIDI'nin duyulan nota dizisinde değil, art arda gelen pitch-bend olaylarındaki iki değerin sıralamasına ikili veri olarak gömülmüştür.
