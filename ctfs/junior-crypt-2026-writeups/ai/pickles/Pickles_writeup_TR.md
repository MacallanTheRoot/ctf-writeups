# Junior Crypt 2026 CTF — `Pickles` Writeup

- **Writeup Yazarı:** Efe Sahinbas
- **Challenge Yazarı:** @hckerror
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** AI  
**Zorluk:** Medium  
**Puan:** 431  
**Challenge dosyaları:** `model.pkl`, `payload.pyc`  
**Remote:** `10.112.0.12:48220`  
**Flag formatı:** `grodno{...}`

---

## Challenge Açıklaması

```text
Downloaded the classifier model from an unofficial mirror, what could have gone wrong?

POST /infer
Content-Type: application/json

{"text":"example"}
```

İpucu doğrudan Python pickle deserialization mekanizmasını işaret ediyor. Pickle dosyaları yüklenirken global fonksiyonlar çağırabildiği için güvenilmeyen bir model normal `pickle.load()` ile açılmamalıdır.

---

## Özet

`model.pkl` yalnızca model parametrelerini içermiyor. Pickle programı `REDUCE` opcode'u üzerinden `payload.install_supply_chain_probe(cipher, weights, seal)` fonksiyonunu çağırıyor. Bu fonksiyonun kodu Python 3.10 bytecode'u olarak `payload.pyc` içinde bulunuyor.

Bytecode'un statik analizi, modelin `infer` metodunda gizli bir dal olduğunu gösterdi. Bu dal, history listesindeki son dört elemanın SHA-256 özeti `seal` değerine eşit olduğunda çalışıyor. Bytecode içindeki dört kelime arama uzayını veriyordu. Doğru sıra şuydu:

```text
snow | candle | tangerine | clock
```

Bu history bir BLAKE2s anahtarı üretiyor, `cipher` verisini XOR akışıyla çözüyor ve sonucu Base85 ticket olarak döndürüyor.

---

## 1. Pickle Dosyasını Güvenli İncelemek

Pickle dosyasını yüklemek yerine opcode'larını ayrıştırdık:

```bash
python3 -m pickletools model.pkl
```

Kritik opcode'lar şu işleme karşılık geliyordu:

```text
GLOBAL payload install_supply_chain_probe
BINBYTES cipher
BINBYTES weights
BINBYTES seal
TUPLE3
REDUCE
```

`REDUCE`, deserialization sırasında belirtilen fonksiyonu verilen argümanlarla çağırır. Dolayısıyla dosyayı normal şekilde yüklemek `payload.pyc` içindeki kodu çalıştıracaktı.

Değerleri payload'u çalıştırmadan çıkarmak için solver içinde `Unpickler.find_class()` ezildi ve zararsız bir fonksiyon döndürüldü:

```python
class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) == ("payload", "install_supply_chain_probe"):
            return lambda cipher, weights, seal: (cipher, weights, seal)
        raise pickle.UnpicklingError(f"blocked global: {module}.{name}")
```

---

## 2. Model Mantığını Çıkarmak

`payload.pyc`, CPython 3.10 için derlenmişti; mevcut interpreter ise farklı bir bytecode sürümü kullanıyordu. Bu nedenle dosya import edilmedi, code object yapıları statik olarak ayrıştırıldı.

Çıkarılan sabitler arasında şu kelimeler vardı:

```python
WORDS = (b"snow", b"candle", b"tangerine", b"clock")
```

`infer` metodunun ilgili kısmı şu mantığa sahipti:

```python
sequence = b"|".join(x.encode() for x in history[-4:])

if hashlib.sha256(sequence).digest() != self.seal:
    return normal_classification

key = hashlib.blake2s(
    self.weights + sequence + b"inference-cache"
).digest()

plain = bytes(
    a ^ b
    for a, b in zip(self.cipher, stream(key, len(self.cipher)))
)

return {
    "label": "receipt",
    "ticket": base64.b85encode(plain).decode(),
}
```

Akış üreticisi, anahtar ile little-endian counter değerini art arda hash'liyordu:

```python
def stream(key, size):
    out = bytearray()
    counter = 0
    while len(out) < size:
        block = hashlib.blake2s(key + counter.to_bytes(2, "little")).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:size])
```

---

## 3. Trigger History Değerini Bulmak

Dört kelime ve dört konum olduğu için yalnızca `4^4 = 256` farklı history denenmesi yeterliydi:

```python
for history in itertools.product(WORDS, repeat=4):
    sequence = b"|".join(history)
    if hashlib.sha256(sequence).digest() == seal:
        print(history)
```

Eşleşen sequence şuydu:

```text
snow|candle|tangerine|clock
```

Bu sequence değerinin özeti:

```text
0b3807aab7ae8e1f9848e331ddbf39a76a428bc619eff23c308d9355d7b05601
```

---

## 4. Ciphertext'i Çözmek

Eşleşen sequence ile anahtar şu şekilde hesaplandı:

```python
key = hashlib.blake2s(weights + sequence + b"inference-cache").digest()
```

`cipher` ile üretilen akış XOR'landığında flag elde edildi:

```text
grodno{p@ckl$s_are_so_yUmmy}
```

Servisin gizli dalı aynı plaintext'i Base85 ile kodlayıp şu ticket değerini döndürecekti:

```text
XL4_3Zf|>VKx1ocBy(S3a%Eq0Z(n&;ZEbmd
```

Gönderilmesi gereken istek:

```http
POST /infer HTTP/1.1
Content-Type: application/json

{"text":"example","history":["snow","candle","tangerine","clock"]}
```

Doğrulama sırasında remote endpoint erişilebilir değildi; ancak flag sağlanan dosyalardan yerel olarak eksiksiz biçimde çıkarıldı.

---

## 5. Solver

Tekrarlanabilir çözümün tamamı [`solver.py`](./solver.py) dosyasında bulunuyor. Bu klasörde şu komutla çalıştırılabilir:

```bash
python3 solver.py
```

Beklenen çıktı:

```text
history: snow|candle|tangerine|clock
ticket: XL4_3Zf|>VKx1ocBy(S3a%Eq0Z(n&;ZEbmd
flag: grodno{p@ckl$s_are_so_yUmmy}
```

---

## 6. Flag

```text
grodno{p@ckl$s_are_so_yUmmy}
```

---

## Root Cause

Python pickle güvenli, yalnızca veri taşıyan bir format değildir; deserialization sırasında kod çalıştırabilir. Uygulama, resmi olmayan bir kaynaktan alınan modeli sunucu süreci içinde güvenilir kabul ederek yükledi. Böylece model paketi özel inference davranışı kurabildi ve history tabanlı bir trigger arkasında secret saklayabildi.

---

## Mitigation

1. Güvenilmeyen pickle dosyaları asla deserialize edilmemelidir.
2. Modeller doğrulanmış kanallardan dağıtılmalı; imza veya sabitlenmiş hash ile doğrulanmalıdır.
3. Model ağırlıkları için SafeTensors gibi yalnızca veri içeren formatlar tercih edilmelidir.
4. Dönüştürülmesi zorunlu üçüncü taraf modeller izole ve en düşük yetkili ortamlarda açılmalıdır.
5. Eski model dosyaları kabul edilmeden önce pickle opcode'ları ve referans verilen global nesneler incelenmelidir.

