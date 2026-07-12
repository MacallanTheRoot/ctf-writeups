# Junior Crypt 2026 CTF — `Pickles` Writeup

- **Writeup Author:** Efe Sahinbas
- **Challenge Author:** @hckerror
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** AI  
**Difficulty:** Medium  
**Points:** 431  
**Challenge files:** `model.pkl`, `payload.pyc`  
**Remote:** `10.112.0.12:48220`  
**Flag format:** `grodno{...}`

---

## Challenge Description

```text
Downloaded the classifier model from an unofficial mirror, what could have gone wrong?

POST /infer
Content-Type: application/json

{"text":"example"}
```

The hint points directly at Python pickle deserialization. Pickle files can invoke global functions while they are loaded, so an untrusted model must not be opened with a normal `pickle.load()` call.

---

## Summary

`model.pkl` does not contain only model parameters. Its pickle program calls `payload.install_supply_chain_probe(cipher, weights, seal)` through the `REDUCE` opcode. The matching implementation is stored as Python 3.10 bytecode in `payload.pyc`.

Static analysis of that bytecode revealed a hidden branch in the model's `infer` method. The branch activates when the SHA-256 digest of the last four history entries matches `seal`. Four embedded words provided the search space. The correct order was:

```text
snow | candle | tangerine | clock
```

That history derives a BLAKE2s key, decrypts `cipher` with an XOR stream, and returns the result as a Base85 ticket.

---

## 1. Inspecting the Pickle Safely

The pickle was disassembled instead of loaded:

```bash
python3 -m pickletools model.pkl
```

The important opcodes were equivalent to:

```text
GLOBAL payload install_supply_chain_probe
BINBYTES cipher
BINBYTES weights
BINBYTES seal
TUPLE3
REDUCE
```

`REDUCE` calls the referenced function with the supplied arguments during deserialization. Loading this file normally would therefore execute code from `payload.pyc`.

To extract the values without executing the payload, the solver overrides `Unpickler.find_class()` and substitutes a harmless function:

```python
class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) == ("payload", "install_supply_chain_probe"):
            return lambda cipher, weights, seal: (cipher, weights, seal)
        raise pickle.UnpicklingError(f"blocked global: {module}.{name}")
```

---

## 2. Recovering the Model Logic

`payload.pyc` was compiled for CPython 3.10, while the available interpreter used a different bytecode version. Its code objects were therefore parsed statically rather than imported.

The recovered constants included:

```python
WORDS = (b"snow", b"candle", b"tangerine", b"clock")
```

The relevant `infer` logic was equivalent to:

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

The stream generator repeatedly hashes the key and a little-endian counter:

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

## 3. Finding the Trigger History

There are only four embedded words and four positions, so all `4^4 = 256` histories can be tested:

```python
for history in itertools.product(WORDS, repeat=4):
    sequence = b"|".join(history)
    if hashlib.sha256(sequence).digest() == seal:
        print(history)
```

The matching sequence was:

```text
snow|candle|tangerine|clock
```

Its digest is:

```text
0b3807aab7ae8e1f9848e331ddbf39a76a428bc619eff23c308d9355d7b05601
```

---

## 4. Decrypting the Ciphertext

Using the matching sequence, the key is computed as:

```python
key = hashlib.blake2s(weights + sequence + b"inference-cache").digest()
```

XORing `cipher` with the generated stream gives:

```text
grodno{p@ckl$s_are_so_yUmmy}
```

The service's hidden branch would return the same plaintext Base85-encoded as:

```text
XL4_3Zf|>VKx1ocBy(S3a%Eq0Z(n&;ZEbmd
```

The corresponding request is:

```http
POST /infer HTTP/1.1
Content-Type: application/json

{"text":"example","history":["snow","candle","tangerine","clock"]}
```

The remote endpoint was unavailable during verification, but the complete flag was recovered locally from the supplied artifacts.

---

## 5. Solver

The complete reproducible solver is included as [`solver.py`](./solver.py). Run it from this directory:

```bash
python3 solver.py
```

Expected output:

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

Python pickle is a serialization format with code-execution semantics, not a safe data-only format. The application trusted a model from an unofficial source and deserialized it in the server process. This allowed the model package to install custom inference behavior and hide a secret behind a history-dependent trigger.

---

## Mitigation

1. Never deserialize untrusted pickle files.
2. Distribute models through authenticated channels and verify cryptographic signatures or pinned hashes.
3. Prefer data-only formats such as SafeTensors for model weights.
4. Load third-party models in an isolated, least-privileged environment when conversion is unavoidable.
5. Inspect pickle opcodes and referenced globals before accepting legacy model artifacts.

