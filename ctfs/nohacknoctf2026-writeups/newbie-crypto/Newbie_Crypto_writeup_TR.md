# NoHackNoCTF 2026 — Newbie Crypto Writeup

- **Yazar:** Efe Şahinbaş
- **GitHub Deposu:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Kategori:** Crypto  
**Challenge dosyası:** `chal.zip`  
**Flag formatı:** `NHNC{...}`

---

## Challenge Açıklaması

Challenge bize küçük bir dağıtım arşivi veriyordu. Arşivin içinde şifreleme kodu ve bu kodla üretilmiş çıktı dosyaları vardı. Amaç, şifrelenmiş admin ticket’ını çözmek ve içindeki flag’i almaktı.

Arşiv içindeki önemli dosyalar şunlardı:

```text
dist/chall.py
dist/public.txt
dist/output.txt
```

İlk bakışta klasik bir AES sorusu gibi görünüyor. Kod, birkaç guest ticket’ı ve bir admin ticket’ı AES-CTR ile şifreliyor.

Asıl hata ise her ticket için aynı key ve aynı nonce değerinin tekrar kullanılması.

---

## 1. Challenge Kodunu İncelemek

`chall.py` içindeki kritik kısım şifreleme fonksiyonuydu:

```python
KEY = get_random_bytes(16)
NONCE = b"ticket42"


def encrypt(ticket):
    cipher = AES.new(KEY, AES.MODE_CTR, nonce=NONCE)
    return cipher.encrypt(ticket).hex()
```

Key rastgele üretiliyor, fakat nonce sabit. Daha önemlisi, her ticket şifrelenirken aynı `KEY` ve aynı `NONCE` ile yeni bir AES-CTR nesnesi oluşturuluyor.

AES-CTR modunda bu, her mesajın aynı keystream ile şifrelenmesi anlamına gelir.

Challenge’ın temel zafiyeti buydu.

---

## 2. AES-CTR Mantığı

AES-CTR, plaintext’i doğrudan blok blok şifrelemek yerine bir keystream üretir ve plaintext ile XOR’lar:

```text
ciphertext = plaintext XOR keystream
```

Decrypt işlemi de aynı şekilde yapılır:

```text
plaintext = ciphertext XOR keystream
```

Bu yapı yalnızca keystream tekrar kullanılmadığı sürece güvenlidir. CTR modunda aynı key ve nonce tekrar kullanılırsa aynı keystream baştan üretilir.

Bu durumda bir plaintext/ciphertext çiftini biliyorsak keystream’i çıkarabiliriz:

```text
keystream = known_plaintext XOR known_ciphertext
```

Ardından aynı keystream ile şifrelenmiş başka bir ciphertext’i çözebiliriz:

```text
admin_plaintext = admin_ciphertext XOR keystream
```

---

## 3. Guest Ticket Üzerinden Known Plaintext

Challenge bize `public.txt` içinde guest kullanıcıların isimlerini ve koltuklarını veriyor:

```text
name,seat
hsuan0223x,H-0223
NHNC,T-0704
this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read,N-0705
AI_WILL_SLOP,C-114514
```

Guest ticket formatı da `chall.py` içinde açık şekilde görülüyor:

```python
def make_guest_ticket(name, seat):
    return encode_ticket(
        {
            "event": "modern-crypto-101",
            "role": "guest",
            "name": name,
            "seat": seat,
            "note": "enjoy the workshop",
        }
    )
```

Ayrıca JSON çıktısı deterministic, çünkü kodda şu kullanım var:

```python
json.dumps(ticket, separators=(",", ":"))
```

Bu yüzden guest ticket plaintext’lerini birebir yeniden oluşturabiliyoruz.

Özellikle üçüncü guest kaydı çok önemliydi çünkü ismi oldukça uzundu:

```text
this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read
```

Bu plaintext, admin ticket ciphertext’inin tamamını kapsayacak kadar uzun olduğu için tam keystream’i çıkarmak için kullanılabiliyor.

---

## 4. Keystream’i Çıkarmak

`output.txt` içinde guest ciphertext’leri ve admin ciphertext’i veriliyor.

Çözüm planı şu şekilde:

```text
1. guest_cipher_2 için plaintext’i yeniden oluştur.
2. Bu plaintext’i guest_cipher_2 ile XOR’la.
3. Keystream’i elde et.
4. admin_cipher ile keystream’i XOR’la.
5. Admin ticket JSON’unu oku ve flag’i al.
```

Bu yöntem çalışıyor çünkü iki mesaj da aynı AES-CTR keystream’i ile şifrelenmiş.

---

## 5. Solver

```python
import json
import re


def encode_ticket(ticket):
    return json.dumps(ticket, separators=(",", ":")).encode()


def make_guest_ticket(name, seat):
    return encode_ticket(
        {
            "event": "modern-crypto-101",
            "role": "guest",
            "name": name,
            "seat": seat,
            "note": "enjoy the workshop",
        }
    )


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


attendees = [
    ("hsuan0223x", "H-0223"),
    ("NHNC", "T-0704"),
    (
        "this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read",
        "N-0705",
    ),
    ("AI_WILL_SLOP", "C-114514"),
]

with open("dist/output.txt", "r", encoding="utf-8") as f:
    output = f.read()

values = dict(re.findall(r"(guest_cipher_\d|admin_cipher) = ([0-9a-f]+)", output))

known_plaintext = make_guest_ticket(*attendees[2])
known_ciphertext = bytes.fromhex(values["guest_cipher_2"])
admin_ciphertext = bytes.fromhex(values["admin_cipher"])

keystream = xor_bytes(known_plaintext, known_ciphertext)
admin_plaintext = xor_bytes(admin_ciphertext, keystream)

print(admin_plaintext.decode())
```

Script çalıştırıldığında admin ticket açık şekilde elde ediliyor:

```json
{"event":"modern-crypto-101","role":"admin","name":"organizer","seat":"ROOT","note":"priority access granted","flag":"NHNC{c7r_k3y57r34m5_5h0uld_n3v3r_r37urn}"}
```

---

## 6. Flag

```text
NHNC{c7r_k3y57r34m5_5h0uld_n3v3r_r37urn}
```

---

## Root Cause

Zafiyetin temel sebebi AES-CTR nonce reuse hatasıdır.

Program her ticket için yeni AES-CTR nesnesi oluşturuyor, fakat aynı key ve aynı nonce değerini kullanıyor:

```python
cipher = AES.new(KEY, AES.MODE_CTR, nonce=NONCE)
```

CTR modu AES’i stream cipher gibi kullandığı için bu hata tüm mesajların aynı keystream ile şifrelenmesine neden oluyor.

Yeterince uzun bir known plaintext/ciphertext çifti elde edildiğinde keystream çıkarılabiliyor ve aynı keystream ile şifrelenmiş admin ticket çözülebiliyor.

---

## Mitigation

Bu zafiyeti önlemek için:

1. CTR modunda aynı key + nonce çifti asla tekrar kullanılmamalıdır.
2. Her encryption işlemi için benzersiz nonce üretilmelidir.
3. Nonce, ciphertext ile birlikte saklanmalı veya gönderilmelidir.
4. AES-GCM veya ChaCha20-Poly1305 gibi authenticated encryption modları tercih edilmelidir.
5. Mesaj formatının gizli kalmasına güvenilmemelidir.

Daha güvenli bir örnek kullanım:

```python
nonce = get_random_bytes(8)
cipher = AES.new(KEY, AES.MODE_CTR, nonce=nonce)
ciphertext = nonce + cipher.encrypt(ticket)
```

Gerçek sistemlerde buna ek olarak integrity/authentication koruması da kullanılmalıdır.

---

## Son Notlar

Bu challenge basit ama önemli bir crypto hatasını gösteriyordu. AES’in kendisinde bir zafiyet yoktu; problem AES-CTR modunun yanlış kullanılmasından kaynaklanıyordu.

Temel ders şu:

```text
CTR modunda key + nonce tekrar kullanılırsa keystream tekrar kullanılır.
Keystream tekrar kullanılırsa known plaintext ile diğer mesajlar çözülebilir.
```
