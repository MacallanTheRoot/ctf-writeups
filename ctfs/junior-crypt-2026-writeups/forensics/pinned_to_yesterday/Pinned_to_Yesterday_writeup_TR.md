# Junior Crypt 2026 CTF - `Pinned to Yesterday` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **Kategori:** Forensics
- **Zorluk:** Medium

## Amaç

Windows artefaktlarından üç değer isteniyor:

1. `RecentDocs\.pdf` altındaki ilk PDF adı
2. ShellBagsExplorer ile ilişkili `TypedPaths` klasörü
3. Örnek Prefetch içindeki executable adı

Flag biçimi `grodno{pdf_folder_exe}`.

## Registry Analizi

Koleksiyonda birden fazla test hive bulunduğu için yalnız `strings` çıktısına güvenmek yanıltıcıdır. Hive'lar gerçek registry parser ile açılıp şu anahtarlar incelendi:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs\.pdf
HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths
```

Challenge validator'ının kabul ettiği PDF kaydı, `.pdf` altındaki fiziksel ilk kayıt olan:

```text
WhatsNew.2898.pdf
```

TypedPaths içindeki ilgili yolun son klasör bileşeni:

```text
ShellBagsExplorer
```

## Prefetch Analizi

Prefetch dosyası `MAM` sıkıştırmalı olduğundan yalnız ham string araması yeterli değildir. Başlık/dekompresyon sonucunda yürütülebilir dosya adı `CALC.EXE` olarak görülür. Validator'ın beklediği casing `calc.exe` biçimindedir.

Üç parça validator tarafından kabul edilen yazımla birleştirilir:

## Flag

```text
grodno{WhatsNew.2898.pdf_ShellBagsExplorer_calc.exe}
```

## Not

Artefakt setindeki birden fazla hive ve “first” ifadesinin MRU sırası ile fiziksel kayıt sırası arasındaki belirsizliği nedeniyle diğer makul kombinasyonlar reddedildi. Yukarıdaki değer CTF sunucusu tarafından doğrulanmıştır.
