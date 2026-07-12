# Junior Crypt 2026 CTF - `WrongKube++` Writeup

- **Writeup Yazarı:** Efe Şahinbaş
- **Challenge Yazarı:** @vvanuss
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Reverse Engineering  
**Zorluk:** Hard  
**Dosya:** `WrongKube++.exe`  
**SHA-256:** `9eb1d7cd74bdc195df16ab0bdca9a55c2df7d33e0b624c8fa9f38e1bf5ef7509`

---

## Özet

`WrongKube++.exe`, PyQt6 ile hazırlanmış 64-bit bir PyInstaller uygulamasıdır. Python arayüzü Kubernetes benzeri projeyi normalize edip paketteki `wrongkube_validator.dll` dosyasına gönderir. Flag Python bytecode'unda değil, native doğrulayıcının başarı dalında şifreli olarak saklanmıştır.

Final flag:

```text
grodno{wr0ngkub3pp_5p3ctr4l_qu0rum_0v3rdr1v3}
```

## 1. İlk İnceleme

```bash
file 'WrongKube++.exe'
strings -a -el 'WrongKube++.exe'
```

Dosya yaklaşık 36 MB boyutunda bir PE32+ GUI uygulamasıdır. PyInstaller loader mesajları, `python312.dll`, PyQt6 bileşenleri ve aşağıdaki özel artefaktlar görülür:

```text
main
src.ui
src.validator_bridge
assets\demo.wkubeproj
build\wrongkube_validator.dll
PYZ.pyz
```

## 2. PyInstaller Paketini Açmak

Arşiv içeriği PyInstaller'ın kendi aracıyla listelenebilir:

```bash
pyi-archive_viewer -r -b 'WrongKube++.exe'
```

Interactive viewer üzerinden `src.validator_bridge`, demo proje ve DLL çıkarıldı. Bridge bytecode'undaki stringler native API sözleşmesini gösterir:

```python
lib.validate_cluster.argtypes = [ctypes.c_char_p]
lib.validate_cluster.restype = ctypes.c_void_p
```

Node ve edge verileri deterministik JSON'a çevrilerek `validate_cluster()` fonksiyonuna verilir. Fonksiyon sonuç olarak `ok`, `score`, `signature`, `summary` ve `flag` alanları bulunan JSON döndürür.

## 3. Native Validator

DLL export tablosunda temel fonksiyonlar şunlardır:

```text
validate_cluster
free_result
```

`validate_cluster` içindeki başarı kontrolü şu signature değerini bekler:

```asm
cmp r10d, 0x2911e
jne failure
```

Kontrol geçildiğinde `0x18002b310` adresindeki 45 şifreli byte, iki byte'lık turlar halinde özel bir LCG/XOR akışıyla çözülür. Başlangıç sabitleri:

```text
seed    = 0xc5b1d2ff
state_a = 0x47502943
state_b = 0x47502932
state_c = 0x3c6ef35f
```

İlk byte için temel dönüşüm:

```python
stream = seed * 0x19660d + state_c
plain = encrypted ^ (stream >> 16) ^ stream ^ step
```

İkinci byte farklı bir state güncellemesi kullanır. Depodaki `solve.py`, assembly döngüsünü doğrudan yeniden uygular.

## 4. Çözüm

Önce DLL PyInstaller paketinden çıkarılır, ardından:

```bash
python3 solve.py wrongkube_validator.dll
```

Çıktı:

```text
grodno{wr0ngkub3pp_5p3ctr4l_qu0rum_0v3rdr1v3}
```

## Flag

```text
grodno{wr0ngkub3pp_5p3ctr4l_qu0rum_0v3rdr1v3}
```

## Temel Nokta

GUI ve cluster constraint'leri dikkat dağıtıcıdır. Flag, native doğrulayıcının yalnız başarı durumunda çalışan deterministic decrypt döngüsünden bağımsız olarak kurtarılabilir.
