# NoHackNoCTF 2026 — `Flag Checkers` Writeup

- **Author:** Efe Şahinbaş
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Reverse Engineering / Crypto  
**Target:** `flag_checkers`  
**Flag format:** `NHNC{...}`

---

## Challenge Description

The challenge gave us a single executable and the following instruction:

```bash
echo -n "NHNC{...}" | ./flag_checkers
```

The important detail is `echo -n`: the program checks the exact input bytes and the trailing newline must not be included.

---

## Summary

`flag_checkers` is a stripped, statically linked x86-64 ELF binary. It reads a candidate flag from `stdin`, transforms it with an internal validation algorithm, and prints either `Correct` or `Wrong`.

At first glance the binary looks annoying because it uses self-modifying code, a small JIT-like stub, and anti-debug style checks. However, after extracting the real algorithm, the core logic turned out to be an invertible Feistel network. That means the flag does not need to be brute-forced. Instead, the embedded target value can be inverted block by block to reconstruct the original input directly.

Final flag:

```text
NHNC{2b06cc91a6d35aa24e886394ab574e1c4b4f9eed7ad6d7aca7a3228a39cf318f0a3c523a72263b0995f6417f3b5fd56443d482fbd9b430a578c4038a451028b9}
```

---

## 1. Initial Binary Triage

I started with the usual static checks:

```bash
file flag_checkers
```

The binary was identified as a 64-bit x86 ELF, statically linked and stripped:

```text
ELF 64-bit LSB executable, x86-64, statically linked, stripped
```

Since the binary was stripped, useful symbols were not available. `strings` also gave very little useful output:

```bash
strings -a flag_checkers
```

The only immediately relevant strings were:

```text
Correct
Wrong
```

So the binary clearly performs an internal check, but it does not expose the expected flag, length, or format through plain strings.

---

## 2. Self-Modifying Code and Runtime Setup

Disassembling the `.text` section showed that the visible code was relatively small. This was the first sign that the program was constructing or decoding part of its logic at runtime.

At startup, the program allocates a fixed RWX memory region:

```text
mmap(0x30000000, 0x2000, RWX)
```

Then it decodes encrypted bytes from the data section into that region. Two important runtime objects are created there:

```text
0x30001000  -> small JIT-like shellcode stub
0x30000040  -> six 32-bit round constants
```

The decoded shellcode is only a few bytes long:

```asm
ff 14 25 20 00 00 30    call qword ptr [0x30000020]
c1 c0 XX                rol eax, XX
c3                      ret
```

This means the stub calls a function pointer stored at `0x30000020`, then rotates the returned `eax` value left by `XX`.

The important part is that `XX` is modified during execution. In other words, this tiny code block is self-modifying and the rotate amount changes from round to round.

---

## 3. Anti-Debug and Red Herrings

The binary also contains some anti-debug or anti-sandbox style logic.

The most visible part is a double `fork()` check. The result is stored in a global flag and checked during the main loop. In a normal local environment this does not prevent execution, but it adds noise during reverse engineering.

There is also an FNV-1a-looking multiplication pattern using:

```asm
imul eax, eax, 0x1000193
```

At first this looks like a hash check, but after following the data flow it turns out to be a dead-end obfuscation path. The value is effectively reset, so it does not contribute to the flag validation.

The main lesson from this stage was to separate the actual validation path from the code used only to slow analysis down.

---

## 4. Reconstructing the Real Algorithm

After extracting the decoded tables and following the transformation loop, the validation routine became clearer.

The input is handled as fixed-size data:

```text
17 blocks × 8 bytes = 136 bytes
```

The input is zero-padded internally if needed. Each 8-byte block is processed with a chaining key.

The initial key is:

```text
K0 = 0x0F1E2D3C4B5A6978
```

For each block `g`, the program performs:

```text
state = byteswap64(chunk_g) XOR K_g
```

Then `state` is split into two 32-bit halves:

```text
X = low32(state)
Y = high32(state)
```

The pair `(X, Y)` is passed through a 15-round Feistel network.

A simplified round looks like this:

```text
t = f(X XOR rc(r), r)
X_new = Y XOR t
Y_new = X
```

After 15 rounds, the resulting 64-bit value becomes both:

```text
K_{g+1}
```

and the output block that is compared against the embedded target.

This chaining behavior is why the algorithm looks more complex than a simple per-block comparison.

---

## 5. Round Function

The round function uses four 256-byte S-box tables. The table choice depends on the round number:

```python
def table_idx(r):
    return (r * 3 + 1) & 3
```

The rotate amount is also round-dependent:

```python
def rot_amount(r):
    return ((r * 7 + 3) % 31) + 1
```

The round constant is generated from a six-element lookup table and the standard `0x9e3779b9` constant:

```python
def rc(r):
    lookup6 = [
        0xa5a5f00d,
        0x1337beef,
        0x0badc0de,
        0xfaceb00c,
        0xdeadc0de,
        0x8badf00d,
    ]
    return lookup6[r % 6] ^ (((r + 1) * 0x9e3779b9) & 0xffffffff)
```

Each S-box was verified to be a permutation of `0..255`:

```python
sorted(table) == list(range(256))
```

That matters because it confirms that the byte substitution is bijective. Combined with the Feistel structure, this makes the whole transformation reversible.

---

## 6. Why Brute Force Was Not Needed

The key observation is that the target output is embedded inside the binary.

Since the final output consists of 17 blocks, the embedded target gives us the post-Feistel output for every block:

```python
K_next = int.from_bytes(target[g*8:g*8+8], "big")
```

Because this output is also used as the next chaining key, each block can be inverted in order.

A single Feistel round can be reversed like this:

```python
def inverse_round(Xn, Yn, r):
    X = Yn
    t = f(X ^ rc(r), r)
    Y = Xn ^ t
    return X, Y
```

So for each block:

1. Take `K_next` from the target.
2. Reverse rounds `14` down to `0`.
3. Recover the pre-Feistel state.
4. XOR it with the previous chaining key.
5. Apply the reverse byte order to recover the original input block.

The block recovery formula is:

```text
chunk_g = byteswap64(K_g XOR state_before)
```

This reconstructs the flag directly.

---

## 7. Solver Skeleton

The core inversion logic can be summarized as:

```python
K0 = 0x0F1E2D3C4B5A6978

Ks = [K0] + [
    int.from_bytes(target[g*8:g*8+8], "big")
    for g in range(17)
]

flag = b""

for g in range(17):
    X = Ks[g + 1] & 0xffffffff
    Y = Ks[g + 1] >> 32

    for r in reversed(range(15)):
        X, Y = inverse_round(X, Y, r)

    state_before = X | (Y << 32)
    chunk = byteswap64(Ks[g] ^ state_before)
    flag += chunk.to_bytes(8, "little")
```

The full script depends on the extracted S-box tables and target bytes, but the important point is the inversion method. The binary looks like a checker, but structurally it is a reversible block transformation with chaining.

---

## 8. Verification

The recovered flag was tested against the original binary:

```bash
echo -n "NHNC{2b06cc91a6d35aa24e886394ab574e1c4b4f9eed7ad6d7aca7a3228a39cf318f0a3c523a72263b0995f6417f3b5fd56443d482fbd9b430a578c4038a451028b9}" | ./flag_checkers
```

Output:

```text
Correct
```

So the final answer is:

```text
NHNC{2b06cc91a6d35aa24e886394ab574e1c4b4f9eed7ad6d7aca7a3228a39cf318f0a3c523a72263b0995f6417f3b5fd56443d482fbd9b430a578c4038a451028b9}
```

---

## Takeaways

This challenge is a good example of why reverse engineering should not stop at the obfuscation layer.

The binary includes several distracting elements:

- stripped static ELF
- runtime-decoded code
- fixed RWX mapping
- self-modifying rotate instruction
- anti-debug-style `fork()` checks
- misleading hash-like operations

However, the real validation algorithm is clean once extracted. It is a Feistel network with chaining, and because the target output is embedded in the binary, the flag can be recovered by mathematical inversion instead of brute force.

Final flag:

```text
NHNC{2b06cc91a6d35aa24e886394ab574e1c4b4f9eed7ad6d7aca7a3228a39cf318f0a3c523a72263b0995f6417f3b5fd56443d482fbd9b430a578c4038a451028b9}
```
