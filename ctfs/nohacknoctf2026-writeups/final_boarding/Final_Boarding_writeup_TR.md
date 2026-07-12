# NoHackNoCTF 2026 — `Final Boarding` Writeup

- **Yazar:** Efe Şahinbaş
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Misc / OSINT  
**Hedef:** Fotoğraftaki uçak bilgisinden hareketle fotoğraf tarihini ve IATA uçuş numarasını bulmak  
**Flag formatı:** `NHNC{YYYYMMDD_FLIGHT}`

---

## Challenge Metni

> On the last day of the trip, I stood in front of the boarding gate, ready to board my flight home.
>
> That day in Japan marked the end of Golden Week, and the airport was packed with travelers preparing to return home.
>
> Before boarding, I took a photo of the aircraft in front of me; it was the flight I was about to take.
>
> Based on the aircraft information in the photo and the clues in the challenge, find:
>
> - The date the photo was taken
> - The IATA flight number of the flight I boarded
>
> Flag format: `NHNC{YYYYMMDD_FLIGHT}`
>
> Please use the IATA flight number, such as `BR198`, not the ICAO callsign.

---

## Kısa Özet

Bu challenge, tek bir havaalanı fotoğrafındaki uçak bilgilerini kullanarak doğru uçuşu ve tarihi bulmayı gerektiriyordu. Görselde uçağın operatörü, tescil numarası ve model bilgisi okunabiliyordu. Challenge metnindeki “Golden Week’in son günü” ipucu ise tarih aralığını daraltmak için kullanıldı.

Fotoğraftaki uçak Jetstar Japan’a ait `JA06JJ` tescilli bir Airbus A320 idi. Havalimanı ortamı ve uçuş rotası birlikte değerlendirildiğinde aday uçuş Jetstar Japan’ın Osaka Kansai’den Taipei Taoyuan’a giden `GK55` uçuşu olarak eşleşti.

Sonuç:

```text
Date: 2026-05-05
IATA Flight Number: GK55
Flag: NHNC{20260505_GK55}
```

---

## 1. Fotoğraftaki Görsel İpuçları

İlk adım, fotoğrafta doğrudan okunabilen bilgileri çıkarmaktı.

![Final Boarding challenge image](./images/Final_boarding.png)

Fotoğrafta dikkat çeken bilgiler:

```text
Airline / Operator: Jetstar Japan
Aircraft Registration: JA06JJ
Aircraft Type: Airbus A320
Airport Context: Kansai International Airport-like apron and terminal environment
```

Uçağın gövdesinde ve kuyruk kısmında Jetstar logosu açıkça görülüyor. Gövde üzerindeki tescil numarası ise `JA06JJ` olarak okunabiliyor. Bu bilgi, OSINT tarafında en güçlü başlangıç noktasıydı; çünkü uçak tescil numarası belirli bir airframe’i doğrudan işaret eder.

---

## 2. Aircraft Registration Üzerinden Daraltma

Uçak tescili:

```text
JA06JJ
```

Bu tescil Jetstar Japan filosundaki bir Airbus A320’ye karşılık gelir. Bu aşamada amaç, bu uçağın challenge metnindeki tarih ipucuna yakın dönemde hangi uçuşlarda kullanıldığını bulmaktı.

OSINT akışı şu şekilde ilerledi:

```text
1. Fotoğraftan registration değerini oku: JA06JJ
2. JA06JJ için uçuş geçmişi / uçak takip kayıtlarını kontrol et
3. Golden Week sonu tarih aralığını filtre olarak kullan
4. Eşleşen rotaları ve uçuş numaralarını karşılaştır
```

Bu yöntem, rastgele Jetstar Japan uçuşları arasında arama yapmak yerine doğrudan fotoğraftaki uçağa odaklanmayı sağladı.

---

## 3. Tarih İpucu: Golden Week’in Sonu

Challenge metnindeki kritik cümle şuydu:

```text
That day in Japan marked the end of Golden Week.
```

Golden Week, Japonya’da Nisan sonu ile Mayıs başındaki ulusal tatillerden oluşan yoğun seyahat dönemidir. Bu yüzden “Golden Week’in son günü” ifadesi, fotoğrafın Mayıs başındaki dönüş yoğunluğu sırasında çekildiğini gösteriyordu.

Bu ipucu sayesinde tarih aralığı şu döneme daraltıldı:

```text
Late April — early May 2026
```

Challenge çözümünde kullanılan tarih:

```text
2026-05-05
```

Flag formatında bu tarih şu şekilde yazılır:

```text
20260505
```

> Not: Bu writeup’ta tarih, dosyanın EXIF bilgisinden değil; challenge metni, Golden Week ipucu ve uçuş eşleştirmesi üzerinden çıkarılmıştır.

---

## 4. Havalimanı ve Rota Eşleştirmesi

Fotoğraftaki apron düzeni, terminal/jet bridge yapısı, yer hizmetleri araçları ve Jetstar Japan operasyon bağlamı, görüntünün Osaka Kansai International Airport ile uyumlu olduğunu gösteriyordu.

Aday rota şu şekilde daraldı:

```text
Departure: Osaka Kansai International Airport (KIX)
Arrival: Taipei Taoyuan International Airport (TPE)
Airline: Jetstar Japan
Flight: GK55
```

Jetstar Japan’ın `GK55` uçuşu, IATA formatında yazıldığında doğrudan şu değere karşılık gelir:

```text
GK55
```

Burada önemli nokta, challenge’ın ICAO callsign değil IATA flight number istemesiydi. Bu nedenle `JJP55` gibi ICAO/callsign formatı değil, `GK55` kullanılmalıdır.

---

## 5. Neden `GK55`?

Fotoğraftaki uçak `JA06JJ` tescilli Jetstar Japan Airbus A320 idi. Uçuş geçmişi ve rota kontrolü yapıldığında bu uçağın Golden Week sonu döneminde Osaka Kansai — Taipei Taoyuan hattındaki Jetstar Japan uçuşuyla eşleştiği görüldü.

Bu eşleşmede kullanılan ana veriler:

```text
Registration: JA06JJ
Operator: Jetstar Japan
Aircraft: Airbus A320
Route: KIX → TPE
IATA Flight Number: GK55
```

Bu nedenle flag içinde kullanılacak uçuş numarası:

```text
GK55
```

---

## 6. Flag’in Oluşturulması

Challenge’ın istediği format:

```text
NHNC{YYYYMMDD_FLIGHT}
```

Bulunan değerler:

```text
YYYYMMDD = 20260505
FLIGHT   = GK55
```

Final flag:

```text
NHNC{20260505_GK55}
```

---

## Sonuç

Bu challenge’ın çözümü üç ana parçaya dayanıyordu:

```text
1. Fotoğraftaki uçak tescilini okumak: JA06JJ
2. Bu tescili Jetstar Japan Airbus A320 ile eşleştirmek
3. Golden Week ipucu ve uçuş geçmişi üzerinden doğru IATA uçuş numarasını bulmak
```

Sonuç olarak doğru flag:

```text
NHNC{20260505_GK55}
```
