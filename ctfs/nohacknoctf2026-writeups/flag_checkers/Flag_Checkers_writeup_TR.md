# NoHackNoCTF 2026 — `Flag Checkers` Writeup

- **Yazar:** Efe Şahinbaş
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Reverse Engineering / Crypto  
**Hedef:** `flag_checkers`  
**Flag formatı:** `NHNC{...}`

---

## Soru İçeriği

Challenge bize tek bir çalıştırılabilir dosya veriyor ve flag’i şu şekilde test etmemizi söylüyor:

```bash
echo -n "NHNC{...}" | ./flag_checkers
```

Buradaki önemli nokta `echo -n` kullanılması. Program girdiyi birebir byte seviyesinde kontrol ettiği için sona `\n` karakteri eklenmemeli.

---

## Özet

`flag_checkers`, stripped ve statik linklenmiş bir x86-64 ELF dosyası. Program `stdin` üzerinden aldığı flag adayını içerideki doğrulama algoritmasından geçiriyor ve sonuç doğruysa `Correct`, yanlışsa `Wrong` yazdırıyor.

İlk bakışta binary karmaşık görünüyor. Self-modifying code, küçük bir JIT benzeri stub ve anti-debug tarzı kontroller var. Ancak gerçek algoritma çıkarıldığında yapının aslında tersine çevrilebilir bir Feistel ağı olduğu anlaşılıyor.

Bu nedenle brute-force yapmaya gerek kalmadı. Binary içine gömülü hedef çıktıdan geriye doğru giderek flag doğrudan hesaplandı.

Final flag:

```text
NHNC{2b06cc91a6d35aa24e886394ab574e1c4b4f9eed7ad6d7aca7a3228a39cf318f0a3c523a72263b0995f6417f3b5fd56443d482fbd9b430a578c4038a451028b9}
```

---

## 1. İlk Binary İncelemesi

Başlangıçta klasik kontrolleri yaptım:

```bash
file flag_checkers
```

Binary şu şekilde tanımlanıyordu:

```text
ELF 64-bit LSB executable, x86-64, statically linked, stripped
```

Dosya stripped olduğu için sembol isimleri yoktu. `strings` çıktısı da çok az bilgi veriyordu:

```bash
strings -a flag_checkers
```

Dikkat çeken tek anlamlı string’ler şunlardı:

```text
Correct
Wrong
```

Yani programın içeride bir doğrulama yaptığı belliydi, fakat beklenen flag, uzunluk veya format plain text olarak görünmüyordu.

---

## 2. Self-Modifying Code ve Runtime Kurulum

`.text` bölümü incelendiğinde görünen kodun beklenenden küçük olduğu fark edildi. Bu, programın bazı mantıkları çalışma zamanında çözdüğünü veya oluşturduğunu düşündürdü.

Program başta sabit bir adrese RWX bellek ayırıyor:

```text
mmap(0x30000000, 0x2000, RWX)
```

Daha sonra `.data` bölümündeki şifreli baytları çözerek bu alana yazıyor. Burada iki önemli yapı oluşuyor:

```text
0x30001000  -> küçük JIT benzeri shellcode
0x30000040  -> 6 elemanlı 32-bit round sabiti tablosu
```

Çözülen shellcode çok kısa:

```asm
ff 14 25 20 00 00 30    call qword ptr [0x30000020]
c1 c0 XX                rol eax, XX
c3                      ret
```

Bu stub, `0x30000020` adresindeki fonksiyon pointer’ını çağırıyor ve dönen `eax` değerini `XX` kadar sola döndürüyor.

Önemli nokta şu: `XX` byte’ı her round’da program tarafından yeniden yazılıyor. Bu yüzden kod küçük ama self-modifying davranış gösteriyor.

---

## 3. Anti-Debug ve Yanıltıcı Kodlar

Binary içinde bazı anti-debug veya anti-sandbox benzeri kontroller de bulunuyor.

En görünür olanı çift `fork()` kontrolü. Sonuç global bir değişkende tutuluyor ve ana döngü sırasında kontrol ediliyor. Normal bir yerel ortamda bu programın çalışmasını engellemiyor, ama reverse engineering sırasında gürültü oluşturuyor.

Ayrıca FNV-1a hash’ini andıran bir çarpma deseni de var:

```asm
imul eax, eax, 0x1000193
```

İlk bakışta bu bir hash doğrulaması gibi duruyor. Ancak veri akışı takip edildiğinde bunun gerçek doğrulama yoluna anlamlı katkı sağlamadığı, obfuscation amaçlı bir yan yol olduğu görülüyor.

Bu aşamadaki ana amaç, gerçek flag kontrolünü bu yanıltıcı katmanlardan ayırmaktı.

---

## 4. Gerçek Algoritmanın Çıkarılması

Runtime’da çözülen tablolar ve dönüşüm döngüsü incelendiğinde algoritma daha net hale geldi.

Program girdiyi sabit boyutlu bloklar halinde işliyor:

```text
17 blok × 8 byte = 136 byte
```

Girdi kısa kalırsa içeride sıfır byte ile dolduruluyor. Her 8 byte’lık blok bir zincirleme anahtarı ile işleniyor.

Başlangıç anahtarı:

```text
K0 = 0x0F1E2D3C4B5A6978
```

Her blok `g` için önce şu işlem yapılıyor:

```text
state = byteswap64(chunk_g) XOR K_g
```

Sonra `state` iki 32-bit parçaya ayrılıyor:

```text
X = low32(state)
Y = high32(state)
```

Bu `(X, Y)` çifti 15 round’luk bir Feistel ağına giriyor.

Basitleştirilmiş round yapısı:

```text
t = f(X XOR rc(r), r)
X_new = Y XOR t
Y_new = X
```

15 round sonunda elde edilen 64-bit değer hem bir sonraki bloğun anahtarı oluyor:

```text
K_{g+1}
```

hem de hedef değerle karşılaştırılacak çıktı bloğu olarak kullanılıyor.

Bu zincirleme yapı, algoritmanın basit bir blok karşılaştırmasından daha karmaşık görünmesine sebep oluyor.

---

## 5. Round Fonksiyonu

Round fonksiyonu dört adet 256 byte’lık S-box tablosu kullanıyor. Hangi tablonun seçileceği round numarasına bağlı:

```python
def table_idx(r):
    return (r * 3 + 1) & 3
```

Rotate miktarı da round numarasına göre belirleniyor:

```python
def rot_amount(r):
    return ((r * 7 + 3) % 31) + 1
```

Round sabiti, 6 elemanlı lookup tablosu ve `0x9e3779b9` sabiti ile oluşturuluyor:

```python
def rc(r):
    lookup6 = [
        0xa5a5f00d,
        0x1337beef,
        0x0badc0de,
        0xfaceb00c,
        0xdeadc0de,
        0x8badf00d,
    ]
    return lookup6[r % 6] ^ (((r + 1) * 0x9e3779b9) & 0xffffffff)
```

Her S-box’ın `0..255` aralığında birebir permütasyon olduğu doğrulandı:

```python
sorted(table) == list(range(256))
```

Bu önemliydi, çünkü S-box’ların bijektif olması ve Feistel yapısı birlikte düşünüldüğünde dönüşümün tersine çevrilebilir olduğunu gösteriyor.

---

## 6. Neden Brute-force Gerekmedi?

Kritik gözlem şuydu: hedef çıktı binary’nin içine gömülüydü.

Final çıktı 17 bloktan oluştuğu için her blok için post-Feistel değer doğrudan hedeften alınabiliyor:

```python
K_next = int.from_bytes(target[g*8:g*8+8], "big")
```

Bu çıktı aynı zamanda bir sonraki blok için zincirleme anahtarı olarak kullanıldığı için, bloklar sırayla tersine çevrilebiliyor.

Tek bir Feistel round’unu tersine çevirmek şu şekilde mümkün:

```python
def inverse_round(Xn, Yn, r):
    X = Yn
    t = f(X ^ rc(r), r)
    Y = Xn ^ t
    return X, Y
```

Her blok için süreç şu hale geliyor:

1. `K_next` değerini hedef çıktıdan al.
2. Round’ları `14`ten `0`a doğru ters çalıştır.
3. Feistel öncesi `state` değerini elde et.
4. Bu değeri `K_g` ile XOR’la.
5. Byte sırasını geri çevirerek orijinal input bloğunu çıkar.

Blok kurtarma formülü:

```text
chunk_g = byteswap64(K_g XOR state_before)
```

Bu işlem 17 blok için sırayla uygulandığında flag doğrudan elde ediliyor.

---

## 7. Solver Mantığı

Çözümün ana kısmı şu şekilde özetlenebilir:

```python
K0 = 0x0F1E2D3C4B5A6978

Ks = [K0] + [
    int.from_bytes(target[g*8:g*8+8], "big")
    for g in range(17)
]

flag = b""

for g in range(17):
    X = Ks[g + 1] & 0xffffffff
    Y = Ks[g + 1] >> 32

    for r in reversed(range(15)):
        X, Y = inverse_round(X, Y, r)

    state_before = X | (Y << 32)
    chunk = byteswap64(Ks[g] ^ state_before)
    flag += chunk.to_bytes(8, "little")
```

Tam script için extracted S-box tabloları ve hedef byte dizisi gerekiyor. Fakat çözümün asıl noktası bu: programı brute-force etmek yerine, binary içindeki hedef değer tersine çevriliyor.

---

## 8. Doğrulama

Elde edilen flag binary ile test edildi:

```bash
echo -n "NHNC{2b06cc91a6d35aa24e886394ab574e1c4b4f9eed7ad6d7aca7a3228a39cf318f0a3c523a72263b0995f6417f3b5fd56443d482fbd9b430a578c4038a451028b9}" | ./flag_checkers
```

Çıktı:

```text
Correct
```

Dolayısıyla final cevap:

```text
NHNC{2b06cc91a6d35aa24e886394ab574e1c4b4f9eed7ad6d7aca7a3228a39cf318f0a3c523a72263b0995f6417f3b5fd56443d482fbd9b430a578c4038a451028b9}
```

---

## Çıkarımlar

Bu challenge, obfuscation katmanına takılmadan gerçek doğrulama yapısını bulmanın önemini gösteriyor.

Binary şu dikkat dağıtıcı unsurları içeriyor:

- stripped ve statik ELF yapı
- runtime’da çözülen kod
- sabit RWX memory mapping
- self-modifying rotate instruction
- anti-debug tarzı `fork()` kontrolleri
- hash gibi görünen ama işlevsiz yan yollar

Ancak gerçek algoritma çıkarıldığında yapı oldukça temizdi. Bir Feistel ağı ve zincirleme mekanizması kullanılıyordu. Hedef çıktı binary içinde gömülü olduğu için flag, brute-force yerine doğrudan matematiksel tersine çevirme ile üretilebildi.

Final flag:

```text
NHNC{2b06cc91a6d35aa24e886394ab574e1c4b4f9eed7ad6d7aca7a3228a39cf318f0a3c523a72263b0995f6417f3b5fd56443d482fbd9b430a578c4038a451028b9}
```
