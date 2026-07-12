# Junior Crypt 2026 CTF - `WrongKube+++` Writeup

- **Yazar:** @vvanuss
- **Kategori:** Reverse Engineering
- **Zorluk:** Nightmare+
- **Dosya:** `WrongKube+++.exe`
- **SHA-256:** `ac8addb97b5cf22b73442c864d7ab6c8f6ad8c0c0aa8ed94edfdea23b9f200f4`

## Özet

`WrongKube+++.exe`, PyQt6 arayüzüne sahip 64-bit bir PyInstaller uygulaması. Python katmanı Kubernetes benzeri bir projeyi JSON'a dönüştürüp `wrongkube_validator.dll` adlı native DLL'e gönderiyor. Paket içindeki demo proje, kabul edilen topolojiye özellikle çok yakın hazırlanmış.

Doğrulayıcının tüm aşamalarını assembly seviyesinde tersine çevirmek yerine DLL ve demo projeyi çıkardım, export edilen doğrulama fonksiyonunu doğrudan çağırdım ve ayrıntılı skor alanlarını oracle olarak kullandım. Dört düzeltmeden sonra DLL canonical topolojiyi kabul ederek flag'i döndürdü.

## 1. İlk İnceleme

```bash
file 'WrongKube+++.exe'
rabin2 -I 'WrongKube+++.exe'
rabin2 -S 'WrongKube+++.exe'
```

Dosya, büyük bir overlay içeren PE32+ GUI uygulamasıydı. Dosyanın sonundaki string'ler PyInstaller paketini ve önemli bileşenleri gösteriyordu:

```text
assets\demo.wkubeproj
build\wrongkube_validator.dll
base_library.zip
PYZ.pyz
python312.dll
```

Native DLL iki önemli fonksiyon export ediyor:

```text
validate_cluster
free_result
```

Sonuç yapısı da DLL string'leri içinde görülebiliyordu:

```json
{"ok":false,"score":0,"signature":0,"summary":"...","flag":"",...}
```

## 2. PyInstaller Paketinin Çıkarılması

GUI'yi çalıştırmadan PyInstaller'ın kendi okuyucusu kullanılabilir:

```python
from PyInstaller.archive.readers import CArchiveReader

archive = CArchiveReader("WrongKube+++.exe")
for name in (
    "assets\\demo.wkubeproj",
    "build\\wrongkube_validator.dll",
    "PYZ.pyz",
):
    with open(name.replace("\\", "_"), "wb") as output:
        output.write(archive.extract(name))
```

`PYZ.pyz` içindeki `src.validator_bridge` modülünün Python 3.12 bytecode'u disassemble edildiğinde DLL'e gönderilen JSON sözleşmesi ortaya çıktı.

Her node şu alanlara düzleştiriliyor:

```text
id, type, name, namespace, labels, selector, replicas, port, mount
```

Her edge ise şu alanları içeriyor:

```text
source_id, target_id, binding, role, port
```

## 3. Native Doğrulayıcının Çağrılması

Eklenen [`call_validator.c`](./call_validator.c) yardımcısı Windows DLL'ini yükleyerek dönen JSON'u ekrana yazdırıyor. Linux üzerinde cross-compile edilebilir:

```bash
x86_64-w64-mingw32-gcc -O2 \
  -o call_validator.exe call_validator.c
```

Programı Wine içinde çalıştırdım. Doğru formata çevrilmiş fakat değiştirilmemiş demo şu sonucu verdi:

```json
{
  "ok": false,
  "score": 150,
  "signature": 811730,
  "summary": "Control plane is close. Northbound, audit, specter, and oracle lanes still disagree.",
  "flag": "",
  "manifest": 28,
  "edges": 60,
  "meta": 23,
  "shadow": 15,
  "specter": 13,
  "phantom": 11
}
```

Her değişiklikten sonra ayrıntılı sayaçlar okunabildiği için bu yöntem GUI'den çok daha kullanışlıydı.

## 4. Bozuk Kaynakların Bulunması

31 node'un her birini sırayla silip `manifest` değerindeki değişimi karşılaştırdım. Başlangıç skoruna katkı vermeyen üç node şunlardı:

```text
dep-specter
svc-specter
pod-veil
```

Projedeki tutarsızlıklar:

1. `specter-daemon`, diğer specter kaynakları ve containment edge'i `specter-net` gösterirken `audit-lane` namespace'indeydi.
2. `specter-svc` portu `9444`, route ve expose edge portları ise `9555` idi.
3. `veil-1`, `specter-map` mount'unu kullanıyordu; canonical topolojide specter secret'ını kullanması gerekiyordu.

Doğru node özellikleri:

```text
dep-specter.namespace = specter-net
svc-specter.port      = 9555
pod-veil.mount        = specter-key
```

Bu değişikliklerden sonra `manifest=31` oldu ancak oracle aşaması hâlâ başarısızdı. Eksik son ilişki şu mount edge'iydi:

```text
sec-specter -> pod-veil
binding = mount
role    = specter-key
port    = 0
```

Eklenen [`solve.py`](./solve.py), dört değişikliği çıkarılan demo projeye uygular ve DLL'in beklediği düzleştirilmiş payload'u üretir.

## 5. Kabul Edilen Sonuç

Düzeltilmiş payload ile doğrulayıcı şu sonucu döndürdü:

```json
{
  "ok": true,
  "score": 158,
  "signature": 890544,
  "summary": "Abyssal control plane reconciled. Sextuple witness accepted.",
  "manifest": 31,
  "edges": 61,
  "meta": 24,
  "shadow": 16,
  "specter": 14,
  "phantom": 12,
  "vm": 9,
  "vm2": 8,
  "vm3": 7,
  "vm4": 6,
  "vm5": 8,
  "vm6": 7
}
```

## Flag

```text
grodno{wr0ngkub3ppp_4by55_0r4cl3_qu0rum_3xtr3m3}
```

## Temel Nokta

Challenge, GUI ve çok katmanlı türetilmiş kontroller arkasına gizlenmiş bir constraint recovery problemiydi. Native doğrulayıcının ayrıntılı sayaç ve özetler döndürmesi, hatalı node ve ilişkileri bulmak için güçlü bir oracle sağladı.
