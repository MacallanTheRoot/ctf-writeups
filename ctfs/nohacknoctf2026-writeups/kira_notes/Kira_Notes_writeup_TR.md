# NoHackNoCTF 2026 — `Kira-Notes` Writeup

- **Yazar:** Efe Şahinbaş
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Forensics  
**Challenge dosyası:** `places.sqlite`  
**Flag formatı:** `NHNC{...}`

---

## Challenge İçeriği

> Please don't use AI to solve this question  
> Learn instead of letting the agent do it :(  
> What is the category? Once you play it, you will know.

Challenge tek bir Firefox artefaktı ile başlıyordu: `places.sqlite`. İlk bakışta bu dosya sadece tarayıcı geçmişi gibi görünüyordu. Fakat geçmiş kayıtları incelendiğinde zincir GitHub deposuna, oradan Proton Drive paylaşımına ve en sonunda bir disk imajına gidiyordu. Flag doğrudan `places.sqlite` içinde değildi; disk imajındaki silinmiş dosyalardan kurtarılması gerekiyordu.

---

## Kısa Özet

Çözüm zinciri şu şekilde ilerledi:

```text
places.sqlite
    -> Firefox tarayıcı geçmişi
    -> GitHub deposu: Kira-Notes
    -> Proton Drive paylaşımı
    -> of.img disk imajı
    -> silinmiş/kurtarılmış ZIP + PNG + PDF
    -> parola rekonstrüksiyonu
    -> şifreli ZIP’in açılması
    -> flag.txt
```

Final flag:

```text
NHNC{n0w_y0u_kn0w_h0w_t0_f0r3ns1c_0x00000Easyyyyyyyyy}
```

---

## 1. `places.sqlite` Dosyasını İncelemek

Firefox; tarayıcı geçmişini, sayfa başlıklarını, ziyaret bilgilerini ve bazı diğer kayıtları SQLite veritabanlarında saklar. Bu challenge için en önemli tablo `moz_places` tablosuydu. Bu tabloda ziyaret edilen URL’ler ve sayfa başlıkları bulunur.

İlk olarak veritabanını açıp ilgili URL kayıtlarını listeledim:

```bash
sqlite3 places.sqlite
```

```sql
SELECT id, url, title
FROM moz_places
ORDER BY id;
```

Normal YouTube ve arama kayıtları arasında asıl dikkat çeken kısım GitHub, Proton Drive ve küçük bir web arşivine giden izlerdi:

```text
25|https://github.com/UmmItKin|UmmItKin (UmmIt Kin, Leon) · GitHub
26|https://github.com/UmmItKin?tab=repositories|UmmItKin (UmmIt Kin, Leon) / Repositories · GitHub
27|https://github.com/ICEDTEACTF|ICEDTEA CTF · GitHub
28|https://github.com/orgs/ICEDTEACTF/repositories|ICEDTEACTF repositories · GitHub
29|https://github.com/UmmItKin/Kira-Notes|GitHub - UmmItKin/Kira-Notes · GitHub
43|https://proton.me/|Proton: Privacy by default
44|https://drive.proton.me/urls/00MNVW0SHG#do4wWWpAQ0Lw|Kira-Notes - Proton Drive
45|http://151.158.224.74:31337/|Kira Notes // Retro Hacker Archive
46|http://151.158.224.74:31337/wtfbro|404 Not Found
47|http://151.158.224.74:31337/#guestbook|Kira Notes // Retro Hacker Archive
48|http://151.158.224.74:31337/dl/eyeswap.bin|404 Not Found
49|http://151.158.224.74:31337/dl/notebook-crack.tgz|404 Not Found
```

Bu noktada anlaşılan şey şuydu: `places.sqlite` final cevabı vermiyordu, bizi diğer artefaktlara götüren bir harita görevi görüyordu.

---

## 2. GitHub ve Proton Drive İzini Takip Etmek

GitHub deposu doğrudan flag içermiyordu. Asıl işlevi, bizi Proton Drive paylaşımına yönlendirmekti.

![Proton Drive Paylaşımı](./assets/kira-notes1.png)

Proton Drive klasöründe üç dosya öne çıkıyordu:

```text
noth*****.png
of.img
Some Backup 01.png
```

Kısmen gizlenmiş PNG dosyası önemliydi çünkü üzerinde elle yazılmış ve parola gibi görünen bir metin parçası vardı.

![Parola Parçası](./assets/kira-notes2.png)

Bu noktadan sonra ana hedef `of.img` oldu. Çünkü en büyük dosya oydu ve forensics challenge için asıl verinin disk imajı içinde olması bekleniyordu.

---

## 3. `of.img` Disk İmajını Analiz Etmek

Disk imajını indirdikten sonra bölüm yapısını kontrol ettim:

```bash
fdisk -l of.img
mmls of.img
```

İmajda Linux dosya sistemi vardı ve bölüm `2048` sektöründen başlıyordu. Her sektör `512` byte olduğu için mount offset’i şöyle hesaplandı:

```text
2048 * 512 = 1048576
```

Dosya sistemini read-only olarak mount ettim:

```bash
sudo mkdir -p /mnt/of
sudo mount -o ro,loop,offset=1048576 of.img /mnt/of
```

Ardından kullanıcının Downloads dizinine baktım:

```bash
find /mnt/of/home/ctf/Downloads -ls
```

Canlı dosya sisteminde birkaç adet sıfır byte dosya vardı:

```text
I
will
not
let
you
see
it
```

Sıralı okunduğunda şu cümleyi veriyordu:

```text
I will not let you see it
```

Bu açıkça gerçek dosyaların silindiğini veya unallocated space içinde saklandığını gösteren bir ipucuydu.

---

## 4. Silinmiş Dosyaları Kurtarmak

Görünen dosya sistemi neredeyse boş olduğu için file carving aşamasına geçtim. Amaç, disk imajındaki silinmiş dosyaları kurtarmaktı.

```bash
photorec of.img
```

PhotoRec birkaç önemli dosya kurtardı:

```text
f0541698_flag.zip
f0541700.png
f1017858.pdf
report.xml
```

Kurtarılan dosya isimleri oturuma göre değişebilir. Burada önemli olan dosya türleriydi:

```text
şifreli bir ZIP arşivi
kurtarılmış bir PNG görseli
kurtarılmış bir PDF notu
```

Ayrıca ham imaj içinde flag referansı olup olmadığını kontrol ettim:

```bash
strings -a of.img | grep -i flag
```

Bu komut, imaj içinde `flag.txt` referansının bulunduğunu doğruladı.

---

## 5. Kurtarılan PDF Notunu Okumak

Kurtarılan PDF içinde Kira tarafından bırakılmış bir not vardı:

![Kurtarılan PDF Notu](./assets/kira-notes3.png)

```text
You already have everything you need.

If you cannot pull it out, then you are not built for this.
Do not waste my time looking for answers I have already left for you.

- By Kira
```

Bu not, çözüm için dışarıdan bruteforce veya alakasız tahmin gerekmediğini gösteriyordu. Gerekli parola ve şifreli arşiv zaten mevcut artefaktların içindeydi.

---

## 6. ZIP Parolasını Bulmak

Proton Drive’daki PNG parolanın ilk kısmını gösteriyordu. Disk imajından kurtarılan PNG ise parolanın tam halini ortaya çıkardı.

![Kurtarılan Parola Görseli](./assets/kira-notes4.png)

Tam parola şu şekildeydi:

```text
0x0kira1337
```

Bu değer, iki görseldeki ipuçları birleştirilerek elde edildi.

---

## 7. Şifreli ZIP’i Açmak

Kurtarılan ZIP arşivi parola korumalıydı. Bu yüzden elde edilen parola ile `7z` kullanarak arşivi açtım:

```bash
7z x -p0x0kira1337 f0541698_flag.zip
```

Açma işlemi tamamlandıktan sonra arşivden `flag.txt` çıktı.

```bash
cat flag.txt
```

Çıktı:

```text
NHNC{n0w_y0u_kn0w_h0w_t0_f0r3ns1c_0x00000Easyyyyyyyyy}
```

---

## 8. Flag

```text
NHNC{n0w_y0u_kn0w_h0w_t0_f0r3ns1c_0x00000Easyyyyyyyyy}
```

---

## Sonuç ve Çıkarımlar

Bu challenge tek bir dosyanın içinde gizlenmiş basit bir string bulma sorusu değildi. Asıl çözüm, artefaktlar arasındaki ilişkiyi takip etmekti:

```text
1. Browser history dış bağlantı zincirini verdi.
2. Proton Drive paylaşımı disk imajını ve parola parçasını verdi.
3. Mount edilen dosya sistemi yanıltıcı ama anlamlı bir mesaj gösterdi.
4. Silinmiş dosyalar file carving ile kurtarıldı.
5. Parola iki görselden yeniden oluşturuldu.
6. Şifreli ZIP içindeki flag.txt final cevabı verdi.
```

Bu challenge’daki temel hata, disk imajını mount ettikten sonra görünen boş dosya sisteminde takılı kalmak olurdu. Asıl veri, silinmiş dosyalar ve unallocated space içindeydi.
