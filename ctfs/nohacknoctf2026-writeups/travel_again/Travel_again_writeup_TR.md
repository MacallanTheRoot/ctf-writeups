# NoHackNoCTF 2026 — `Travel again` Writeup

- **Yazar:** Efe Şahinbaş
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** OSINT  
**Zorluk:** 500  
**Hedef:** Fotoğraftaki nesnenin konumunu bulmak  
**Flag formatı:** `NHNC{latitude,longitude}`  
**Koordinat kuralı:** Enlem ve boylam 4 ondalık basamağa truncate edilmeli. Yuvarlama yapılmamalı.

---

## Soru İçeriği

> I snapped a photo while passing through a location during my trip. Since the car never stopped, the photo is all I have. I've forgotten where it was—can you identify the location?
>
> Flag format: `NHNC{latitude,longitude}`  
> Truncate both the latitude and longitude to 4 decimal places.  
> Example: `NHNC{25.0339,121.5645}`
>
> Hint: `Not the shooting spot — the object itself.`

---

## Kısa Özet

Bu challenge’da hareket halindeki bir araçtan çekilmiş karlı bir yolculuk fotoğrafı veriliyor. İlk bakışta fotoğraf oldukça boş görünüyor: geniş bir kar alanı, uzakta dağlar, küçük bir kemerli yapı ve ön tarafta küçük bir tabela/platform benzeri nesne.

Challenge’daki en kritik ipucu şuydu:

```text
Not the shooting spot — the object itself.
```

Yani aranan koordinat, fotoğrafın çekildiği nokta veya aracın bulunduğu yol değil. Flag için istenen koordinat, kadrajda görünen nesnenin kendi konumu.

Bu yüzden çözümde fotoğrafın çekildiği yeri değil, görüntüdeki nesneyi hedef aldım. Görsel eşleştirme ve çevresel doğrulama sonucunda konum Japonya’nın Hokkaido bölgesinde, Shikaoi çevresindeki bir çiftlik yapısıyla eşleşti.

Son koordinat:

```text
43.1849,143.0325
```

Final flag:

```text
NHNC{43.1849,143.0325}
```

---

## 1. Fotoğrafı Okumak

Fotoğrafta görülen temel ipuçları şunlardı:

![Challenge Görseli](./images/travel_again.jpg)

Dikkat çeken öğeler:

- Geniş, karla kaplı açık arazi
- Uzakta alçak dağ silsilesi
- Kırsal ve tarımsal bir çevre
- Küçük, kemerli/yarım silindir çatılı bir yapı
- Yapının ön tarafında küçük bir tabela veya platform
- Yoğun şehir dokusunun olmaması
- Okunabilir bir tabela, yol levhası veya mağaza ismi bulunmaması

Fotoğraf doğrudan okunabilir bir konum bilgisi vermediği için çözüm metin okumadan çok görsel geolocation üzerine kuruluydu.

Buradaki en değerli ipucu, kar alanının ortasında tek başına duran nesneydi. Kar, dağlar ve geniş tarım arazisi bölgeyi daraltmak için yardımcıydı; fakat asıl eşleştirme nesne üzerinden yapılmalıydı.

---

## 2. Hint’i Yorumlamak

Challenge ipucu şu şekildeydi:

```text
Not the shooting spot — the object itself.
```

Bu ipucu çözüm stratejisini tamamen değiştiriyor.

Yanlış yaklaşım, fotoğrafın çekildiği yolu veya aracın tam konumunu bulmaya çalışmak olurdu. Ancak istenen şey kameranın konumu değil, kadrajdaki nesnenin koordinatı.

Bu yüzden doğru yaklaşım şu şekildeydi:

```text
1. Fotoğraftaki ayırt edici nesneyi belirle.
2. Bu nesneyi uydu görüntüsü, harita verisi veya web kaynaklarıyla eşleştir.
3. Çevredeki arazi yapısının fotoğrafla uyumlu olup olmadığını kontrol et.
4. Fotoğrafçının değil, nesnenin koordinatını submit et.
```

---

## 3. Bölgeyi Daraltmak

Fotoğrafın genel atmosferi kuzey Japonya’yı, özellikle Hokkaido’yu işaret ediyordu.

Bunu destekleyen görsel işaretler:

- Yoğun kar örtüsü
- Geniş tarım alanları
- Alçak dağ sıraları
- Kırsal, çiftlik ağırlıklı çevre
- Şehir merkezinden uzak açık arazi yapısı

Son eşleşme, Hokkaido’nun Tokachi bölgesindeki Shikaoi çevresine oturdu. Bu bölge, geniş Tokachi Ovası, tarım arazileri, süt çiftlikleri ve dağ manzaralarıyla fotoğraftaki çevreye uyuyordu.

---

## 4. Nesne Odaklı Arama

Challenge doğrudan “object itself” dediği için aramaya genel manzara terimleriyle başlamak verimsiz olurdu.

Örneğin şu tarz aramalar çok fazla benzer sonuç üretir:

```text
snow field Hokkaido mountains
```

Bunun yerine nesne ve bölgeyi birlikte hedefleyen aramalar daha mantıklıydı:

```text
Hokkaido snow field farm arched barn
Tokachi snow field dairy farm
Shikaoi Hokkaido dairy farm snow
鹿追町 牧場 雪
鹿追町 酪農 牧場
北鹿追 牧場
```

Görseldeki kırsal yapı, karlı çiftlik çevresi ve bölgesel eşleşmeler Shikaoi / Kita-Shikaoi hattına işaret etti. Buradaki ilgili çiftlik kimliği Nakano Farm / 株式会社中野牧場 olarak doğrulandı.

Çiftliğin listelenen adresi:

```text
北海道河東郡鹿追町北鹿追北10線3番地55
```

Bu adres, final flag için kullanılan koordinat bölgesiyle uyuşuyordu.

---

## 5. Doğrulama

Eşleşmeyi doğrulamak için birkaç kontrol kullandım.

### Görsel uyumluluk

Challenge görselinde görülenler:

- Karla kaplı tarım alanı
- Kırsal çiftlik yapısı
- Uzak dağ silsilesi
- Açık ve seyrek Tokachi tarzı arazi

Bu çevre, Shikaoi / Tokachi / Hokkaido hattıyla uyumluydu.

### Coğrafi uyumluluk

Shikaoi, Hokkaido’nun Tokachi bölgesinde yer alır. Bölge geniş tarım alanları, süt çiftlikleri, açık ovalar ve dağ manzaralarıyla bilinir.

### Nesne-konum uyumluluğu

Tespit edilen nesne, Kita-Shikaoi çevresindeki Nakano Farm / 株式会社中野牧場 ile eşleşti.

İlgili adres:

```text
北海道河東郡鹿追町北鹿追北10線3番地55
```

Bu konum için kullanılan koordinat:

```text
43.1849,143.0325
```

---

## 6. Koordinatları Truncate Etmek

Challenge, koordinatların 4 ondalık basamağa truncate edilmesini istiyor. Yani yuvarlama yapılmamalı.

Final koordinat zaten istenen 4 ondalık basamak formatında:

```text
43.1849,143.0325
```

Flag formatı:

```text
NHNC{latitude,longitude}
```

Yerine koyunca:

```text
NHNC{43.1849,143.0325}
```

---

## 7. Final Flag

```text
NHNC{43.1849,143.0325}
```

---

## Çıkarımlar

Bu challenge, OSINT geolocation sorularında her zaman fotoğrafçının konumunu aramamak gerektiğini gösteren iyi bir örnekti.

En önemli ipucu şuydu:

```text
Not the shooting spot — the object itself.
```

Doğru çözüm akışı:

```text
1. Kamera konumunu değil, nesneyi hedef al.
2. Görseldeki ayırt edici nesneyi arama anchor’ı olarak kullan.
3. Çevresel ipuçlarıyla bölgeyi daralt.
4. Nesnenin konumunu arazi ve kaynaklarla doğrula.
5. Nesnenin koordinatını 4 ondalık basamağa truncate ederek submit et.
```

---

## Doğrulama İçin Kullanılan Kaynaklar

- Nakano Farm resmi şirket bilgileri
- Shikaoi Town üzerindeki 株式会社中野牧場 iş/şirket kaydı
- Shikaoi turizm ve geopark sayfaları üzerinden bölgesel bağlam
