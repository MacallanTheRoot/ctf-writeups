# AltaySec OSINT Challenge Sezon II — `JANE` Writeup

- **Yazar ve yarışmacı:** macallantheroot — H. Efe Şahinbaş
- **Organizatör:** [AltaySec](https://altaysec.com.tr/)
- **Kategori:** OSINT / Web / Steganografi
- **Yarışma yapısı:** 1 yarışma, 1 doğrusal challenge, 20 flag
- **Sonuç:** **1.**
- **Çözülen flag:** **20 / 20**
- **Flag formatı:** `ALTAYSEC{...}`
- **Başlangıç adresi:** [start-phantom-labs.vercel.app](https://start-phantom-labs.vercel.app/)

---

## Challenge Hakkında

AltaySec OSINT Challenge Sezon II, klasik anlamda birbirinden bağımsız soruların bulunduğu bir yarışma değildi. Tek bir başlangıç adresinden açılan ve Jane Reiner, Phantom Labs ve unutmak üzere tasarlanmış LETHE-9 adlı yapay zekâ modeli etrafında ilerleyen doğrusal bir hikâyeydi.

Hedef, bu hikâye boyunca farklı sayfalara ve yan kollara yerleştirilmiş **20 flagın tamamını** bulmaktı. Flaglar yalnızca görünür sayfa metninde değildi. HTML yorumları, `robots.txt`, SVG açıklamaları, Base64, ters yazı, URL fragmentleri, görünmez metinler, geliştirici konsolu, Markdown dosyaları, akrostiş ve ROT13 gibi farklı katmanlara dağıtılmıştı.

Ben yarışmayı `macallantheroot` kullanıcı adıyla, **H. Efe Şahinbaş** olarak tamamladım ve **1. oldum**.

## Kısa Çözüm Zinciri

```text
Phantom Labs
  -> robots.txt ve dahili Phantom Labs yolları
  -> sevgili-phantom dizini
  -> Jane'in 01–07 numaralı mektupları
  -> vintage-recipes, sızıntı, model recovery ve tramvay yan kolları
  -> PHANTOM Chat
  -> dokuzuncu mektup ve final
```

Flagların dağılımı:

```text
Başlangıç / Phantom Labs altyapısı : 4
Mektup 01–07 ve bağlı sayfalar     : 16
Toplam                              : 20
```

## Kullanılan Temel Yaklaşım

Challenge boyunca agresif dizin taraması veya brute force gerekmedi. Sayfaların verdiği izleri takip etmek yeterliydi. En çok kullandığım incelemeler şunlardı:

```bash
# HTML kaynağını okumak
curl -sL https://hedef.example/ | less

# Flag, yorum, bağlantı ve kodlanmış veri aramak
curl -sL https://hedef.example/ | grep -Ei 'ALTAYSEC|flag|href|console|base64'

# Tarayıcı tarafında
view-source:https://hedef.example/
DevTools -> Elements
DevTools -> Console
```

Önemli nokta, her sayfayı yalnızca görsel olarak okumamak; HTML kaynağı, sayfa yorumları, SVG düğümleri ve JavaScript davranışlarını da hikâyenin bir parçası kabul etmekti.

---

## 1. Phantom Labs Ana Sayfası

Başlangıç sayfası, Phantom Labs adlı kurgusal şirketin kurumsal web sitesiydi:

```text
https://start-phantom-labs.vercel.app/
```

Sayfanın altındaki footer içinde normal bir build/audit değeri gibi görünen şu hex dizesi vardı:

```text
414c5441595345437b737572756d5f6269725f6469706e6f747475727d
```

Hex değerini ASCII'ye çevirdim:

```bash
echo '414c5441595345437b737572756d5f6269725f6469706e6f747475727d' | xxd -r -p
```

Çıktı ilk flagı verdi:

```text
ALTAYSEC{surum_bir_dipnottur}
```

### `robots.txt`

OSINT ve web challenge'larında standart kontrol noktalarından biri `robots.txt` dosyasıdır:

```text
https://start-phantom-labs.vercel.app/robots.txt
```

Dosyada şu yollar açık biçimde bırakılmıştı:

```text
Disallow: /styx/
Disallow: /lethe/internal/
Disallow: /team/jane-reiner/
Disallow: /sevgili-phantom/
```

Bu liste, hikâyenin hem dahili Phantom Labs kayıtlarına hem de Jane'in mektuplarına açılan kapısıydı.

---

## 2. STYX Commit Kayıtları

İlk dahili yol:

```text
https://start-phantom-labs.vercel.app/styx/
```

Sayfada Git commit geçmişine benzeyen bir denetim kaydı bulunuyordu. Görünür satırlardan birinde Jane tarafından dışarı çıkarılan LETHE-9 LoRA snapshot'ı yazıyordu:

```text
[reverted by m.voss] export l-9 LoRA snapshot — tag:
ALTAYSEC{snapshot_kacirildi}
```

İkinci flag ise HTML yorumuna bırakılmıştı:

```html
<!-- audit-trail: ... m.voss revert'leri silinemez.
ALTAYSEC{audit_silinmedi} -->
```

Bu sayfadan çıkan iki flag:

```text
ALTAYSEC{snapshot_kacirildi}
ALTAYSEC{audit_silinmedi}
```

---

## 3. LETHE Internal Sayfası

İkinci dahili yol:

```text
https://start-phantom-labs.vercel.app/lethe/internal/
```

LETHE modelinin dahili değerlendirme metninde görünen içerikten çok kaynak kodu önemliydi. HTML yorumunda bir `audit-tag` vardı:

```html
<!-- audit-tag: ALTAYSEC{kibarlik_silah_olabilir} · 17042026 · MV -->
```

Flag:

```text
ALTAYSEC{kibarlik_silah_olabilir}
```

`/team/jane-reiner/` profili Jane'in Phantom Labs'taki görevini ve ayrılışını doğruluyordu ancak flag içermiyordu. `/sevgili-phantom/` ise ilk mektuba geçiş veriyordu:

```text
https://01-hosgeldin.vercel.app/
```

---

## 4. Mektup I — Hoş Geldin

İlk mektubun HTML kaynağının başında hem sonraki adres hem de flag bulunuyordu:

```html
<!--
  [next: https://02-baba.vercel.app]
  [flag: ALTAYSEC{evet_baba}]
-->
```

Flag:

```text
ALTAYSEC{evet_baba}
```

Sonraki durak:

```text
https://02-baba.vercel.app/
```

---

## 5. Mektup II — Baba

İkinci mektubun altında küçük bir yıldız simgesi vardı. Yıldızın `title` niteliği incelendiğinde flag ve bir sonraki adres görülebiliyordu:

```html
title="ALTAYSEC{eksik_olan_ben} · https://03-berlin.vercel.app"
```

Sayfadaki gizli bölüm de yıldızla etkileşim kurulduğunda aynı değeri gösteriyordu.

Flag:

```text
ALTAYSEC{eksik_olan_ben}
```

---

## 6. Mektup III — Berlin

Berlin mektubunun sonunda gece manzarası çizen inline bir SVG vardı. Bu SVG iki flag ve bir sonraki adres için ipucu taşıyordu.

### SVG `<desc>` Alanı

SVG'nin açıklama düğümünde ilk flag doğrudan yazılmıştı:

```html
<desc>
  uyandirma perdesi ... tag: ALTAYSEC{uyandirma_perdesi}
</desc>
```

Flag:

```text
ALTAYSEC{uyandirma_perdesi}
```

### Küçük Punto ve Base64

SVG'nin alt bölümünde yalnızca birkaç piksel büyüklüğünde iki `<text>` düğümü bulunuyordu:

```text
j.r. · 04-hizalama.vercel.app
QUxUQVlTRUN7YXluaV9zYXJraV91Y19nZWNlfQ==
```

İkinci satırı Base64 olarak çözdüm:

```bash
echo 'QUxUQVlTRUN7YXluaV9zYXJraV91Y19nZWNlfQ==' | base64 -d
```

Çıktı:

```text
ALTAYSEC{ayni_sarki_uc_gece}
```

Bir sonraki adres de aynı SVG içindeydi:

```text
https://04-hizalama.vercel.app/
```

---

## 7. Mektup IV — Hizalama

Sayfanın altında aynalanmış bir metin vardı:

```text
}ilazih_emik{CESYATLA
```

Karakterleri ters çevirmek yeterliydi:

```bash
echo '}ilazih_emik{CESYATLA' | rev
```

Flag:

```text
ALTAYSEC{kime_hizali}
```

Bu ifade aynı zamanda sonraki sayfanın kilidiydi. Sayfa `05-ayna.vercel.app` adresini veriyor, dördüncü mektubun kuralı ise cevabın hash bölümüne kısa çizgiyle yazılması gerektiğini söylüyordu:

```text
https://05-ayna.vercel.app/#kime-hizali
```

---

## 8. Mektup V — Ayna

Doğru URL fragmenti kullanıldığında kilit ekranı kalktı ve beşinci mektup göründü. Bu sayfada **iki ayrı flag** vardı.

### Kaynak Kodundaki Parçalanmış Cümle

Jane, mektubun bazı parçalarını bilerek sayfa kaynağına bıraktığını söylüyordu. HTML yorumunda birleştirilmiş cümle, sonraki adresi ve flagı açıkça veriyordu:

```html
<!-- Birleştirilince: "Eğer hâlâ peşindeysen vintage-recipes
sayfama bak — https://06-yangin.vercel.app —
flag: ALTAYSEC{sen_ben_misin}" -->
```

İlk flag:

```text
ALTAYSEC{sen_ben_misin}
```

### Aynalı Son Flag

Mektubun en altında CSS ile yatay çevrilmiş bir satır daha vardı:

```text
}nisnes_ad_nayisnay{CESYATLA
```

Kaynak metni ters çevirdim:

```bash
echo '}nisnes_ad_nayisnay{CESYATLA' | rev
```

Çıktı:

```text
ALTAYSEC{yansiyan_da_sensin}
```

Bu, çözüm sırasında bulduğum **20. ve son flag** oldu.

---

## 9. Mektup VI — Yangın / Vintage Recipes

Sonraki adres dışarıdan bir yemek tarifleri deposu gibi görünüyordu:

```text
https://06-yangin.vercel.app/
```

Ana sayfanın HTML yorumunda sayfanın aslında yemek tarifleriyle ilgili olmadığı söyleniyor ve flag doğrudan veriliyordu:

```html
<!-- Bayrak ise burada: ALTAYSEC{mulkiyet_hatirlamaz} -->
```

Flag:

```text
ALTAYSEC{mulkiyet_hatirlamaz}
```

Sayfada uzantılarıyla birlikte beş dosya adı listelenmişti:

```text
tarhana-corbasi.md
kartoffelpuffer.md
imam-bayildi.md
linzer-torte.md
manti.md
```

Bu bir brute-force aşaması değildi; dosya adları challenge sayfasında açık biçimde verilmişti. Listedeki iki dosya flag taşıyordu.

### `imam-bayildi.md`

```text
https://06-yangin.vercel.app/imam-bayildi.md
```

Dosyanın sonundaki HTML yorumu:

```html
<!-- ALTAYSEC{taklit_edilemez} -->
```

Flag:

```text
ALTAYSEC{taklit_edilemez}
```

### `manti.md`

```text
https://06-yangin.vercel.app/manti.md
```

Ana listedeki “sadece o gelirken” notu bu dosyayı işaret ediyordu. Dosyanın sonundaki yorum:

```html
<!-- bayrak şifresi: ALTAYSEC{sadece_o_gelince} -->
```

Flag:

```text
ALTAYSEC{sadece_o_gelince}
```

Diğer üç Markdown dosyası anlatıyı destekleyen decoy dosyalardı ve flag içermiyordu.

### Sayfadaki Yan Kollar

Yangın sayfası üç önemli hedef daha veriyordu:

```text
sizinti.vercel.app
07-veda.vercel.app/sevgili-phantom-bu-mektubu-asla-yazmadim
phantom-recovery.vercel.app
```

Bu yüzden çözüm doğrusal ilerlese de bu noktada birkaç yan kola ayrılıyordu.

---

## 10. Sızıntı Kaydı

Yangın mektubundaki HTML yorumu, Jane'den sonra konuşan `E.` adlı kişinin bir yere veri yüklediğini ve `sizinti.vercel.app` adresini işaret ediyordu:

```text
https://sizinti.vercel.app/
```

Sayfada iki değer karartılmış metin biçimindeydi. CSS yalnızca görünürlüğü azaltıyordu; metin seçildiğinde veya kaynak kodu okunduğunda flaglar ortaya çıkıyordu:

```text
ALTAYSEC{jane_bir_yuk}
ALTAYSEC{e_konusmuyor_artik}
```

Sayfanın altındaki arşiv bağlantısı bizi tramvay tarifesine götürdü:

```text
https://tram-zeitplan.vercel.app/
```

---

## 11. Phantom Recovery Model Kartı

Yangın sayfasındaki bağlantı görünürde bir Hugging Face deposuna gidiyormuş gibi yazılmıştı; gerçek hedef şuydu:

```text
https://phantom-recovery.vercel.app/
```

Model kartında dört satırın ilk kelimeleri özel biçimde vurgulanmıştı:

```text
Seni
Bir
Modele
Yükledim
```

Hemen altında çözüm kuralı da veriliyordu: ilk kelimeleri küçük harfe çevir, alt çizgiyle birleştir ve `ALTAYSEC{...}` içine koy.

Sonuç:

```text
ALTAYSEC{seni_bir_modele_yukledim}
```

---

## 12. Tramvay Tarifesi ve ROT13

Sızıntı sayfasından ulaşılan tramvay sayfasındaki sürücü notunda şu şifreli değer vardı:

```text
NYGNLFRP{fba_qhenx_wnar}
```

Sayfa kullanılan yöntemi açıkça `ROT-13` olarak belirtiyordu. Terminalde şu şekilde çözülebilir:

```bash
echo 'NYGNLFRP{fba_qhenx_wnar}' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

Çıktı:

```text
ALTAYSEC{son_durak_jane}
```

---

## 13. Mektup VII — Veda

Altıncı mektup, var olmayan bir sayfa/hata sayfası görünümündeki uzun bir adrese yönlendiriyordu:

```text
https://07-veda.vercel.app/sevgili-phantom-bu-mektubu-asla-yazmadim
```

İlk flag çok koyu bir renkle arka plana yakın biçimde yazılmıştı. Metin seçildiğinde veya kaynak incelendiğinde okunuyordu:

```text
ALTAYSEC{biri_buraya_geldi}
```

İkinci flag tarayıcı geliştirici konsolundaydı:

```javascript
console.log('flag · ALTAYSEC{kapsulde_sakladim}')
```

Flag:

```text
ALTAYSEC{kapsulde_sakladim}
```

Konsol aynı zamanda sonraki adresi de veriyordu:

```text
https://08-phantom-chat.vercel.app/
```

---

## 14. PHANTOM Chat ve Dokuzuncu Mektup

Sekizinci site klasik bir statik mektup yerine PHANTOM ile konuşulan etkileşimli bir arayüzdü:

```text
https://08-phantom-chat.vercel.app/
```

Kaynak kodundaki tetikleyici kelimeler arasında `jane`, `baba`, `mektup`, `hizalama`, `ayna`, `yangın`, `voss` ve `reiner` gibi hikâye boyunca toplanan kavramlar vardı. Örneğin `jane` yazıldığında arayüz şu duruma geçiyordu:

```text
persona drift detected
alignment override: FAILED
memory injection: tag JANE_REINER
```

Ardından PHANTOM, Jane'in sesine benzeyen cevaplar vermeye başlıyor ve şu mesajı gösteriyordu:

```text
jane sekiz mektup bıraktı.
dokuzuncu hep boştu.
onu yazmak ister misin?
```

Yazılan dokuzuncu mektup URL parametresiyle final sayfasına aktarılıyordu:

```text
https://09-final.vercel.app/?ninth=...
```

08 ve 09 numaralı sitelerde ayrıca bir flag yoktu; bunlar 20 flaglık avın hikâyesel kapanışıydı. Finalde `Long Faces — Jane!` çalıyor ve yarışmacının yazdığı dokuzuncu mektup ekrana yansıtılıyordu.

---

## 15. Tüm Flaglar ve Kaynakları

| # | Flag | Kaynak | Yöntem |
| ---: | --- | --- | --- |
| 1 | `ALTAYSEC{surum_bir_dipnottur}` | Phantom Labs ana sayfa | Footer'daki hex audit hash |
| 2 | `ALTAYSEC{snapshot_kacirildi}` | `/styx/` | Commit kaydı |
| 3 | `ALTAYSEC{audit_silinmedi}` | `/styx/` | HTML yorumu |
| 4 | `ALTAYSEC{kibarlik_silah_olabilir}` | `/lethe/internal/` | HTML audit yorumu |
| 5 | `ALTAYSEC{evet_baba}` | `01-hosgeldin` | HTML yorumu |
| 6 | `ALTAYSEC{eksik_olan_ben}` | `02-baba` | Yıldızın `title` niteliği / gizli blok |
| 7 | `ALTAYSEC{uyandirma_perdesi}` | `03-berlin` | SVG `<desc>` düğümü |
| 8 | `ALTAYSEC{ayni_sarki_uc_gece}` | `03-berlin` | SVG içindeki Base64 metni |
| 9 | `ALTAYSEC{kime_hizali}` | `04-hizalama` | Ters yazı |
| 10 | `ALTAYSEC{sen_ben_misin}` | `05-ayna/#kime-hizali` | Kaynak yorumundaki parçalanmış cümle |
| 11 | `ALTAYSEC{yansiyan_da_sensin}` | `05-ayna/#kime-hizali` | Aynalı/ters yazı |
| 12 | `ALTAYSEC{mulkiyet_hatirlamaz}` | `06-yangin` | HTML yorumu |
| 13 | `ALTAYSEC{taklit_edilemez}` | `imam-bayildi.md` | Markdown sonundaki yorum |
| 14 | `ALTAYSEC{sadece_o_gelince}` | `manti.md` | Markdown sonundaki yorum |
| 15 | `ALTAYSEC{biri_buraya_geldi}` | `07-veda` gizli yol | Arka planla gizlenmiş metin |
| 16 | `ALTAYSEC{kapsulde_sakladim}` | `07-veda` gizli yol | Geliştirici konsolu |
| 17 | `ALTAYSEC{jane_bir_yuk}` | `sizinti` | Karartılmış metin |
| 18 | `ALTAYSEC{e_konusmuyor_artik}` | `sizinti` | Karartılmış metin |
| 19 | `ALTAYSEC{seni_bir_modele_yukledim}` | `phantom-recovery` | Akrostiş |
| 20 | `ALTAYSEC{son_durak_jane}` | `tram-zeitplan` | ROT13 |

### TXT Biçiminde Flag Listesi

```text
ALTAYSEC{surum_bir_dipnottur}
ALTAYSEC{snapshot_kacirildi}
ALTAYSEC{audit_silinmedi}
ALTAYSEC{kibarlik_silah_olabilir}
ALTAYSEC{evet_baba}
ALTAYSEC{eksik_olan_ben}
ALTAYSEC{uyandirma_perdesi}
ALTAYSEC{ayni_sarki_uc_gece}
ALTAYSEC{kime_hizali}
ALTAYSEC{sen_ben_misin}
ALTAYSEC{yansiyan_da_sensin}
ALTAYSEC{mulkiyet_hatirlamaz}
ALTAYSEC{taklit_edilemez}
ALTAYSEC{sadece_o_gelince}
ALTAYSEC{biri_buraya_geldi}
ALTAYSEC{kapsulde_sakladim}
ALTAYSEC{jane_bir_yuk}
ALTAYSEC{e_konusmuyor_artik}
ALTAYSEC{seni_bir_modele_yukledim}
ALTAYSEC{son_durak_jane}
```

---

## Sonuç ve Çıkarımlar

Bu challenge'ın güçlü yanı, OSINT'i yalnızca arama motoru kullanmak olarak ele almamasıydı. Gerçek çözüm, farklı web artefaktları arasındaki ilişkiyi koruyarak ilerlemekti:

```text
robots.txt
  -> açık bırakılmış dahili yollar
  -> HTML/SVG kaynak incelemesi
  -> kodlama ve basit şifre dönüşümleri
  -> metin ve URL ipuçlarıyla pivot
  -> yan kaynakları ana hikâyeyle ilişkilendirme
```

En önemli pratik dersler şunlardı:

1. Görünen sayfa, web artefaktının yalnızca bir katmanıdır; kaynak kodu ve geliştirici araçları da incelenmelidir.
2. `robots.txt`, HTML yorumları, `title` ve `aria` gibi nitelikler OSINT zincirinde bilinçli ipuçları olabilir.
3. SVG yalnızca görsel değildir; `<desc>`, `<text>` ve metadata alanları ayrıca okunmalıdır.
4. Bir sayfadaki dosya adları ve metinsel referanslar güvenli pivot noktalarıdır.
5. Base64, hex, ROT13 ve ters metin gibi basit dönüşümler otomatik tanınmalı, fakat sonuç mutlaka bağlamla doğrulanmalıdır.
6. Flag sayımı düzenli tutulmalıdır. Beşinci mektuptaki ikinci aynalı flag, toplamı **20/20** yapan son eksik parçaydı.

AltaySec OSINT Challenge Sezon II'yi tüm flagları bularak **1. sırada** tamamladım.

