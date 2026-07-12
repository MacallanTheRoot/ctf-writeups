# NoHackNoCTF 2026 — `Homework` Writeup

- **Author:** Efe Şahinbaş
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Pwn / Crypto  
**Difficulty:** 490  
**Target:** `http://chal3.teagod.tech:8000/`  
**Flag format:** `NHNC{...}`

---

## Challenge Prompt

> Bro's trying to use his homework to make a challenge.  
> `http://chal3.teagod.tech:8000/`

The challenge archive contained a static PIE ELF binary and a Docker setup that exposed the program through `socat`. At first glance, it looked like a normal pwn task, but the actual solution was closer to a hybrid between memory corruption and numerical cryptography.

The final exploit does not overwrite a return address or build a ROP chain. Instead, it abuses a subtle out-of-bounds write in a custom matrix operation, leaks the parameters of a hidden numerical transformation, mathematically inverts that transformation, and sends the decoded answer back to the service.

---

## 1. Initial Triage

After extracting the archive, the relevant files were:

```text
chal/
├── chall
├── Dockerfile
├── docker-compose.yml
└── flag.txt
```

Basic inspection of the binary showed that it was stripped and built as a static PIE executable:

```bash
file chall
```

```text
ELF 64-bit LSB pie executable, x86-64, static-pie linked, stripped
```

The Dockerfile also showed that the challenge was intended to run as a restricted `ctf` user through `socat`:

```text
CMD ["socat", "-T120", "TCP-LISTEN:11111,reuseaddr,fork", "EXEC:/home/ctf/chall,stderr"]
```

So the binary was the main target. There were no source files, debug symbols, or direct hints in the archive.

---

## 2. Understanding the Program Interface

Running the binary locally showed that the program asks for two matrix dimensions, matrix data, and an operation name.

A malformed quick run already leaked useful debug information:

```text
X size:
Y size:
[debug] sizeof(Real) = 128
[debug] X row 0 = ... mod128=0
[debug] Y row 0 = ... mod128=0
[debug] A[0][0] = ... mod128=0
[debug] A[0][1] = ... mod128=0
[debug] from Y row 0 to A[0][1]:
        byte_delta     = 384
        slot_delta     = 3
        slot_remainder = 0
        use shift      = 3
```

This was the first important clue. The program was printing internal heap layout information, and the `shift = 3` value showed how far one matrix row was from another internal slot.

At a high level, the program does the following:

1. Reads two matrix sizes.
2. Allocates and fills two matrices.
3. Lets the user choose an operation.
4. Computes a result matrix.
5. Runs the result through a hidden verification routine.
6. Prints the flag if the computed value matches the expected target.

The usual matrix operations were not enough to reach the target. The interesting branch was the custom operation named `blend`.

---

## 3. The Bug: `blend` Out-of-Bounds Write

The `blend` operation behaves incorrectly when the input matrices are small, especially with `1x1` matrices.

Because each `Real` object occupies `128` bytes and the internal rows are aligned in predictable slots, the debug output reveals that a controlled index can step outside the intended matrix cell and land in a neighboring internal structure.

The important value was:

```text
use shift = 3
```

By choosing the `blend` operation with this shift value, the program can be pushed into writing into an adjacent heap slot.

This is not used like a classic pwn bug. The goal is not to hijack RIP. The goal is to modify the numerical state used by the checker so that the program exposes enough values to reverse the hidden transformation.

In other words, the memory bug is the entry point, but the final solve is mathematical.

---

## 4. The Numerical Structure

Once the `blend` path is triggered correctly, the program prints several high-precision decimal values. The relevant ones are:

```text
n = ...
a_plus_d = ...
bc = ...
```

These values are not random debug noise. They describe a hidden `2x2` matrix transformation.

The transformation can be modeled approximately as:

```text
A ~= [[trace, B],
      [c,     0]]
```

where:

```python
B = Decimal("1e90")
```

and:

```python
c = bc / B
```

The program is effectively applying a large power of this matrix to encoded coordinates. The visible output is the result of applying `A^n` to the original data.

So the challenge becomes:

```text
Given A^n * plaintext_vector = output_vector,
recover plaintext_vector.
```

Since the program gives us enough information to reconstruct the transformation, we can compute the inverse matrix and apply `A^-n` to recover the original text.

---

## 5. Inverting the Transformation

For a matrix of the approximate form:

```text
A = [[s, B],
     [c, 0]]
```

where:

```text
s = a_plus_d
c = bc / B
```

an inverse form can be constructed as:

```python
inv = (
    Decimal(0),
    Decimal(1) / c,
    Decimal(1) / B,
    -s / bc
)
```

Then the inverse power is computed:

```python
inv_n = mpow(inv, n)
```

The encoded output coordinates are multiplied by this inverse matrix power. The result gives back byte values, which can then be converted into ASCII.

The key point is that this avoids brute force entirely. Once the mathematical model is recovered, the remaining work is deterministic.

---

## 6. Exploit Flow

The final exploit follows this sequence:

```text
1. Start the program with 1x1 matrix dimensions.
2. Fill the matrices with controlled values.
3. Select the custom blend operation.
4. Use shift = 3 to reach the useful adjacent slot.
5. Read the printed decimal parameters.
6. Extract n, a_plus_d, and bc.
7. Reconstruct the hidden 2x2 transformation.
8. Compute the inverse power of the matrix.
9. Decode the output coordinates back into text.
10. Send the decoded answer to the remote service.
11. Receive the flag.
```

A simplified version of the important solver logic looks like this:

```python
from decimal import Decimal, getcontext

getcontext().prec = 300

B = Decimal("1e90")

# Values parsed from the program output
n = ...
s = Decimal(a_plus_d)
bc = Decimal(bc_value)

c = bc / B

# Matrix inverse of approximately [[s, B], [c, 0]]
inv = (
    Decimal(0),
    Decimal(1) / c,
    Decimal(1) / B,
    -s / bc,
)

inv_n = mpow(inv, n)

# Apply inv_n to the printed coordinates and recover ASCII
decoded = []
for x, y in encoded_points:
    px, py = mat_vec_mul(inv_n, (Decimal(x), Decimal(y)))
    decoded.append(chr(int(px)))
    decoded.append(chr(int(py)))

answer = ''.join(decoded)
```

The exact implementation depends on how the coordinates are parsed from the service output, but the core idea is the same: rebuild the inverse transformation and decode the target string.

---

## 7. Result

After recovering the expected input and sending it to the service, the program returned the flag:

```text
NHNC{y0u_c4nt_di4g0n4l1z3_y0ur_w4y_0ut_0f_h0m3w0rk_2d6851fe6b5640949a2b44f4800ce1a8}
```

---

## 8. Takeaways

This challenge was not a standard buffer overflow or ROP problem. The vulnerability was memory-corruption-related, but the actual solve required understanding the mathematical checker behind the binary.

The important lessons were:

```text
- Debug output can leak more than addresses; it can leak structure.
- A small OOB write can be enough even without control-flow hijacking.
- Not every pwn challenge ends with RIP control.
- Numerical transformations are often reversible if enough parameters leak.
- High-precision arithmetic matters when the binary works with very large decimal values.
```

Final flag:

```text
NHNC{y0u_c4nt_di4g0n4l1z3_y0ur_w4y_0ut_0f_h0m3w0rk_2d6851fe6b5640949a2b44f4800ce1a8}
```
