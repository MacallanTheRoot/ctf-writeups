# NoHackNoCTF 2026 — `Homework` Writeup

- **Yazar:** Efe Şahinbaş
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Pwn / Crypto  
**Zorluk:** 490  
**Hedef:** `http://chal3.teagod.tech:8000/`  
**Flag formatı:** `NHNC{...}`

---

## Challenge İçeriği

> Bro's trying to use his homework to make a challenge.  
> `http://chal3.teagod.tech:8000/`

Challenge arşivinde statik PIE olarak derlenmiş bir ELF binary ve bu binary’yi `socat` ile servis eden bir Docker kurulumu vardı. İlk bakışta klasik bir pwn sorusu gibi görünse de çözüm, doğrudan ROP veya heap exploitation üzerine kurulu değildi.

Asıl çözüm iki parçadan oluşuyordu:

```text
1. blend operasyonundaki out-of-bounds yazma davranışını kullanmak
2. Programın kullandığı gizli sayısal dönüşümü tersine çevirmek
```

Yani memory corruption kısmı sadece kapıyı açıyor. Flag’e giden asıl yol, programın arka tarafta kurduğu 2x2 matris dönüşümünü matematiksel olarak geri çözmekten geçiyor.

---

## 1. İlk İnceleme

Arşiv çıkarıldığında temel yapı şu şekildeydi:

```text
chal/
├── chall
├── Dockerfile
├── docker-compose.yml
└── flag.txt
```

Binary üzerinde ilk kontrol:

```bash
file chall
```

Çıktı:

```text
ELF 64-bit LSB pie executable, x86-64, static-pie linked, stripped
```

Yani elimizde sembolleri temizlenmiş, statik PIE bir ELF dosyası var. Bu da analizi biraz daha zorlaştırıyor; fakat programın çalışma anında verdiği debug çıktıları çözüm için oldukça önemli ipuçları sağlıyor.

Dockerfile içinde servis akışı da açık şekilde görülüyordu:

```text
CMD ["socat", "-T120", "TCP-LISTEN:11111,reuseaddr,fork", "EXEC:/home/ctf/chall,stderr"]
```

Bu nedenle hedef doğrudan `chall` binary’siydi.

---

## 2. Program Arayüzünü Anlamak

Binary yerelde çalıştırıldığında kullanıcıdan iki matris boyutu, matris elemanları ve bir işlem adı istiyor.

Hatalı veya eksik bir deneme bile şu tarz debug çıktıları veriyordu:

```text
X size:
Y size:
[debug] sizeof(Real) = 128
[debug] X row 0 = ... mod128=0
[debug] Y row 0 = ... mod128=0
[debug] A[0][0] = ... mod128=0
[debug] A[0][1] = ... mod128=0
[debug] from Y row 0 to A[0][1]:
        byte_delta     = 384
        slot_delta     = 3
        slot_remainder = 0
        use shift      = 3
```

Bu çıktı kritik. Program, heap üzerindeki matris satırlarının birbirine göre konumlarını ve `shift = 3` değerini açıkça veriyor.

Genel program akışı şu şekilde modellenebilir:

```text
1. Kullanıcıdan iki matris boyutu alınıyor.
2. İki matris oluşturuluyor ve dolduruluyor.
3. Kullanıcı bir işlem seçiyor.
4. Seçilen işlem sonucunda yeni bir matris üretiliyor.
5. Sonuç gizli bir doğrulama fonksiyonundan geçiyor.
6. Beklenen değer oluşursa flag yazdırılıyor.
```

Normal toplama, çıkarma veya çarpma işlemleri hedefe ulaştırmıyor. Kritik yol, özel `blend` operasyonu.

---

## 3. Kritik Zafiyet: `blend` ile OOB Write

`blend` işlemi küçük matrislerde, özellikle `1x1` boyutlarında, beklenen sınırların dışına yazma davranışı gösteriyor.

Programdaki `Real` yapısının boyutu `128` bayt. Debug çıktısı da satırların bellekte 128 bayt hizalı slotlar halinde durduğunu gösteriyor. Bu yüzden `shift = 3` değeri, bir hücrenin dışına çıkıp komşu bir internal yapıya denk gelmek için kullanılabiliyor.

Önemli nokta şu:

```text
use shift = 3
```

Bu değerle `blend` yolu tetiklendiğinde, programın kendi oluşturduğu komşu bir alan etkilenebiliyor.

Bu klasik anlamda “return address overwrite” değil. Amaç RIP kontrolü almak değil. Amaç, checker’ın kullandığı gizli sayısal yapıyı etkileyip programdan tersine çevrilebilir ara değerler almak.

Dolayısıyla bu challenge’da memory bug, exploit zincirinin başlangıcı; final çözüm ise matematiksel tersine çevirme.

---

## 4. Sayısal Yapının Çözülmesi

`blend` yolu doğru şekilde tetiklendiğinde program yüksek hassasiyetli bazı sayısal değerler basıyor. Çözüm için önemli olanlar:

```text
n = ...
a_plus_d = ...
bc = ...
```

Bunlar rastgele debug verileri değil. Programın kullandığı gizli 2x2 matris dönüşümünü tarif ediyor.

Bu yapı yaklaşık olarak şöyle modellenebiliyor:

```text
A ~= [[trace, B],
      [c,     0]]
```

Burada:

```python
B = Decimal("1e90")
```

ve:

```python
c = bc / B
```

Program, bu matrisi büyük bir üs ile kullanıyor. Yani davranış kabaca şu şekilde düşünülebilir:

```text
A^n * plaintext_vector = output_vector
```

Bize `output_vector` ve `A` matrisini yeniden kurmaya yetecek parametreler verildiği için yapılması gereken şey şudur:

```text
plaintext_vector = A^(-n) * output_vector
```

Bu noktada brute-force gerekmiyor. Dönüşüm matematiksel olarak tersine çevrilebiliyor.

---

## 5. Ters Matris ve Decode

Yaklaşık matris şu formda düşünülebilir:

```text
A = [[s, B],
     [c, 0]]
```

Burada:

```text
s = a_plus_d
c = bc / B
```

Bu matris için ters dönüşüm şu şekilde kurulabiliyor:

```python
inv = (
    Decimal(0),
    Decimal(1) / c,
    Decimal(1) / B,
    -s / bc
)
```

Ardından ters matrisin n’inci kuvveti hesaplanıyor:

```python
inv_n = mpow(inv, n)
```

Programın bastığı koordinatlar bu ters dönüşümden geçirilince orijinal karakter değerleri elde ediliyor. Bu değerler ASCII’ye çevrilerek programın beklediği metin çıkarılıyor.

Özetle:

```text
1. Program bize dönüşümün sonucunu veriyor.
2. Debug değerlerinden dönüşümü yeniden kuruyoruz.
3. Matrisin tersini alıyoruz.
4. Ters dönüşümü uygulayıp plaintext’i geri alıyoruz.
```

---

## 6. Exploit Akışı

Çözüm akışı şu şekilde:

```text
1. Programı 1x1 matris boyutlarıyla başlat.
2. Matrisleri kontrollü değerlerle doldur.
3. blend operasyonunu seç.
4. shift = 3 değerini kullanarak komşu slotu etkile.
5. Programın bastığı Decimal değerleri oku.
6. n, a_plus_d ve bc değerlerini parse et.
7. Gizli 2x2 dönüşümü yeniden kur.
8. Ters matris kuvvetini hesapla.
9. Çıktı koordinatlarını ASCII’ye decode et.
10. Elde edilen metni servise gönder.
11. Flag’i al.
```

Solver’ın temel fikri sadeleştirilmiş haliyle şu şekildeydi:

```python
from decimal import Decimal, getcontext

getcontext().prec = 300

B = Decimal("1e90")

# Program çıktısından parse edilen değerler
n = ...
s = Decimal(a_plus_d)
bc = Decimal(bc_value)

c = bc / B

# Yaklaşık [[s, B], [c, 0]] matrisinin tersi
inv = (
    Decimal(0),
    Decimal(1) / c,
    Decimal(1) / B,
    -s / bc,
)

inv_n = mpow(inv, n)

# Programın bastığı koordinatları geri çöz
decoded = []
for x, y in encoded_points:
    px, py = mat_vec_mul(inv_n, (Decimal(x), Decimal(y)))
    decoded.append(chr(int(px)))
    decoded.append(chr(int(py)))

answer = ''.join(decoded)
```

Asıl exploit scriptinde servis çıktısını parse etme ve cevabı otomatik gönderme kısmı da bulunuyor. Ancak çözümün özü yukarıdaki ters matris mantığı.

---

## 7. Sonuç

Beklenen metin çözüldükten sonra servise gönderildi ve flag alındı:

```text
NHNC{y0u_c4nt_di4g0n4l1z3_y0ur_w4y_0ut_0f_h0m3w0rk_2d6851fe6b5640949a2b44f4800ce1a8}
```

---

## 8. Çıkarım

Bu challenge klasik bir buffer overflow sorusu değildi. Zafiyet bellek taşması tarafında başlıyor, fakat flag’e ulaşmak için programın sayısal doğrulama yapısını anlamak gerekiyor.

Ana dersler:

```text
- Debug çıktıları sadece adres değil, algoritma yapısı da sızdırabilir.
- Küçük bir OOB write, control-flow hijack olmadan da yeterli olabilir.
- Her pwn sorusu RIP kontrolüyle bitmez.
- Eğer dönüşüm parametreleri sızıyorsa, büyük sayılarla yapılan kontroller tersine çevrilebilir.
- Decimal / high precision aritmetik bu tarz challenge’larda kritik olabilir.
```

Final flag:

```text
NHNC{y0u_c4nt_di4g0n4l1z3_y0ur_w4y_0ut_0f_h0m3w0rk_2d6851fe6b5640949a2b44f4800ce1a8}
```
