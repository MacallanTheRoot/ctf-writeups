# Junior Crypt 2026 CTF - `Ghost Layers` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Steganography / SVG  
**Challenge dosyası:** `beaver.svg`  
**Zorluk:** Medium  
**Flag formatı:** `grodno{...}`

---

## Challenge Açıklaması

Author: @vvanuss
medium

What stays visible is not always what matters most.

Flag format: grodno{}

---

## Özet

SVG içinde görünen bir beaver çizimi ve silik görünen metin benzeri bir katman var. Buradaki kritik nokta şu: Bu silik katman görünür durumda olsa da çözüm için doğrudan görünen şeye güvenmek yanıltıcı.

SVG sadece render edilmiş haliyle incelenmemeli; XML kaynağı da kontrol edilmeli. Kaynak içinde `<defs>` bölümünde path'lere dönüştürülmüş bir yazı grubu bulunuyor. Bu grup daha sonra clip path ve mask yapısı içinde kullanılıyor.

Bu gizli grup ayrı render edilince flag okunabiliyor:

```text
grodno{9l0ry_t0_Al1v@r1@_9l0ry_t0_b33r}
```

---

## 1. İlk İnceleme

Challenge dosyası normal bir SVG:

```bash
file beaver.svg
```

Çıktı:

```text
beaver.svg: SVG Scalable Vector Graphics image
```

Dosya bitmap görsel, EXIF metadata veya sonuna eklenmiş bir arşiv gibi davranmıyor. Yararlı bilgi XML yapısının içinde.

---

## 2. SVG Kaynağını Aramak

SVG içinde gizleme için sık kullanılan alanları aramak iyi bir başlangıç:

```bash
rg -n "grodno|display|visibility|opacity|hidden|clip|mask|defs|text|path" beaver.svg
```

Dosyada şunlar dikkat çekiyor:

- `<defs>` bölümü
- `id="s17"` olan bir grup
- `#s17` referansı kullanan bir `clipPath`
- Bir `mask`
- Düşük opaklıklı dekoratif geometri

Render edilen görselde beaver ve silik bir metin bandı görülüyor. Fakat ipucu, görünen şeyin her zaman asıl veri olmadığını söylüyor. Bu yüzden kaynak yapısına bakmak gerekiyor.

---

## 3. Gizli Yazı Grubu

`<defs>` içinde path tabanlı bir grup bulunuyor:

```xml
<g id="s17">
  <g transform="translate(62.500,454.000) scale(0.009400,-0.009400)"
     fill="#f8efc9" stroke="#f8efc9" stroke-width="36">
    ...
  </g>
</g>
```

Bu grup daha sonra clip path olarak kullanılıyor:

```xml
<clipPath id="cp4">
  <use href="#s17"/>
</clipPath>
```

Harfler `<text>` node'u olarak saklanmamış. Yazı çok sayıda `<path>` elemanına çevrilmiş. Bu yüzden normal string extraction ile flag doğrudan çıkmıyor.

---

## 4. Grubu Ayrı Render Etmek

Yazıyı okumak için en sağlam yöntem, bu grubu izole edip yüksek kontrastla render etmek.

Örneğin sadece `s17` grubunu ve `<use href="#s17"/>` kullanımını içeren geçici bir SVG oluşturulup render edilebilir:

```bash
magick textalone.svg textalone.png
```

İzole edilen katman şu flag'i gösteriyor:

```text
grodno{9l0ry_t0_Al1v@r1@_9l0ry_t0_b33r}
```

Burada dikkat edilmesi gereken karakter, `t` harfinden sonra gelen karakterin `o` değil sıfır (`0`) olması.

---

## 5. Flag

```text
grodno{9l0ry_t0_Al1v@r1@_9l0ry_t0_b33r}
```

---

## Root Cause

Flag, SVG içinde yazı olarak değil path geometrisi olarak saklanmış ve clip/mask yapısı üzerinden kullanılmış. Yazı path'e dönüştürüldüğü için plain-text arama ile bulunamıyor.
