# NoHackNoCTF 2026 — Newbie Crypto Writeup

- **Author:** Efe Şahinbaş
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Crypto  
**Challenge files:** `chal.zip`  
**Flag format:** `NHNC{...}`

---

## Challenge Description

The challenge provided a small distribution archive containing the encryption script and generated output files. The goal was to recover the hidden admin ticket and extract the flag.

The important files inside the archive were:

```text
dist/chall.py
dist/public.txt
dist/output.txt
```

At first glance, this looks like a standard AES challenge. The implementation uses AES in CTR mode to encrypt several guest tickets and one admin ticket.

The mistake is that every ticket is encrypted with the same key and the same nonce.

---

## 1. Inspecting the Challenge Code

The relevant part of `chall.py` is the encryption function:

```python
KEY = get_random_bytes(16)
NONCE = b"ticket42"


def encrypt(ticket):
    cipher = AES.new(KEY, AES.MODE_CTR, nonce=NONCE)
    return cipher.encrypt(ticket).hex()
```

The key is random, but the nonce is fixed. More importantly, the cipher object is recreated for every ticket with the same `KEY` and the same `NONCE`.

In AES-CTR, this means the same keystream is reused from the beginning for each encrypted message.

This is the core vulnerability.

---

## 2. Understanding AES-CTR

AES-CTR does not encrypt plaintext blocks directly like ECB or CBC. Instead, it generates a keystream and XORs it with the plaintext:

```text
ciphertext = plaintext XOR keystream
```

To decrypt, the same operation is applied again:

```text
plaintext = ciphertext XOR keystream
```

This is secure only if the keystream is never reused. In CTR mode, reusing the same key and nonce causes the exact same keystream to be generated again.

So if we know one plaintext and its ciphertext, we can recover the keystream:

```text
keystream = known_plaintext XOR known_ciphertext
```

Then we can decrypt any other ciphertext encrypted with the same keystream:

```text
admin_plaintext = admin_ciphertext XOR keystream
```

---

## 3. Known Plaintext from Guest Tickets

The challenge gives us `public.txt`, which contains the names and seats of all guest attendees:

```text
name,seat
hsuan0223x,H-0223
NHNC,T-0704
this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read,N-0705
AI_WILL_SLOP,C-114514
```

The guest ticket format is also visible in `chall.py`:

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

Since JSON serialization is deterministic here because of `separators=(",", ":")`, we can reconstruct the exact plaintext for each guest ticket.

The third guest ticket is especially useful because its name is very long:

```text
this_chal_not_need_read_read_read_read_read_read_read_read_read_read_read
```

That known plaintext is long enough to cover the entire admin ticket ciphertext.

---

## 4. Recovering the Keystream

From `output.txt`, we have the encrypted guest tickets and the encrypted admin ticket.

The plan is:

```text
1. Rebuild the plaintext for guest_cipher_2.
2. XOR it with guest_cipher_2.
3. Recover the keystream.
4. XOR admin_cipher with the recovered keystream.
5. Parse the admin ticket and read the flag.
```

This works because both messages were encrypted with the same AES-CTR keystream.

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

Running the script prints the decrypted admin ticket:

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

The vulnerability is nonce reuse in AES-CTR.

The program creates a fresh AES-CTR object for every ticket, but it always uses the same key and same nonce:

```python
cipher = AES.new(KEY, AES.MODE_CTR, nonce=NONCE)
```

Because CTR mode turns AES into a stream cipher, this causes every message to be encrypted with the same keystream.

Once a long enough known plaintext/ciphertext pair is available, the keystream can be recovered and reused to decrypt the admin ticket.

---

## Mitigation

To prevent this issue:

1. Never reuse the same key and nonce pair in CTR mode.
2. Generate a unique nonce for every encryption.
3. Store or transmit the nonce alongside the ciphertext.
4. Prefer authenticated encryption modes such as AES-GCM or ChaCha20-Poly1305.
5. Do not rely on secrecy of the message format when using stream-cipher-like modes.

A safer pattern would be:

```python
nonce = get_random_bytes(8)
cipher = AES.new(KEY, AES.MODE_CTR, nonce=nonce)
ciphertext = nonce + cipher.encrypt(ticket)
```

For real systems, authenticated encryption should also be used to prevent tampering.

---

## Final Notes

This was a straightforward but important crypto challenge. The algorithm itself was not broken; the failure came from using AES-CTR incorrectly.

The key lesson is simple:

```text
In CTR mode, key + nonce reuse means keystream reuse.
Keystream reuse means known plaintext can decrypt other messages.
```
