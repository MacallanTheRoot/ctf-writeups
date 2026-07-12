# Junior Crypt 2026 CTF - `Zakviel` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **Kategori:** Web
- **Zorluk:** Hard

## Özet

Servis Thalassa CMS `0.3.75` kullanıyor ve challenge'a özel bir “legacy archive import” bridge içeriyor. Bridge, import edilen yorum içeriğini filtrelemeden Thalassa macro expansion işlemine gönderdiği için arbitrary file read oluşuyor.

## Keşif

Ana sayfa legacy import protokolünü öne çıkarıyor. Upstream Thalassa kaynak kodu ile servis karşılaştırıldığında bridge'in standart sürümde bulunmadığı görüldü. Özel akışı tetikleyen parametre:

```text
folio=archive-17
```

Bu yol anonim gönderim ve premoderation kontrollerini bypass ederek yorumun doğrudan source tree'ye yazılmasını ve sayfanın yeniden üretilmesini sağlıyor.

## Macro Injection

Thalassa içerikleri `MacroexpandHFContents` üzerinden geçiriyor. Dosya okuyan macro biçimi:

```text
%[readfile:PATH]
```

Bu ifade legacy bridge ile yorum gövdesine konulduğunda generator onu güvenilir template içeriği gibi genişletiyor. Önce `/etc/hostname` okunarak LFI/arbitrary file read doğrulandı.

Generator'ın çalışma dizini `/proc/self/cwd` üzerinden listelendi; private catalogue dosyası belirlendikten sonra aynı `readfile` macro'su ile içerik alındı ve flag çıkarıldı.

## Flag

```text
grodno{aec40f27-0b38-4012-bc63-c1fcadc2d28f}
```

## Root Cause

Güvenilmeyen legacy yorum içeriği, template macro'ları devre dışı bırakılmadan privileged static-site generator'a aktarılıyor.
