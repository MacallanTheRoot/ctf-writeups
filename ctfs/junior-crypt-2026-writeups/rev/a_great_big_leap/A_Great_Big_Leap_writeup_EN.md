# Junior Crypt 2026 CTF - `A Great Big Leap` Writeup

- **Writeup Author:** Efe Şahinbaş
- **Challenge Author:** @meier
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Reverse Engineering  
**Difficulty:** Medium  
**File:** `goingtoofaraway5.exe`  
**SHA-256:** `4250d40739aab526e7b7745820cfc90509135cdb09c868491b0fe53c359d5ac6`

---

## Challenge Hint

The Russian poem repeatedly mentions jumping, briefly standing still, comparing, and measuring how far the path went. These map directly to assembly concepts:

```text
jump       -> jmp / conditional branch
stand      -> nop
compare    -> cmp
path       -> relative branch displacement
```

## 1. Initial Triage

```bash
file goingtoofaraway5.exe
objdump -d -Mintel goingtoofaraway5.exe
```

The artifact is a small stripped 32-bit Windows PE with three sections. Its `.data` section contains a large collection of fake flag-like strings. The program prints several of them and enters misleading loops; none is the answer.

## 2. Jump Distances

An x86 relative branch target is calculated as:

```text
target = address_after_instruction + signed_displacement
```

Therefore, the traveled distance is:

```text
distance = abs(target - address_after_instruction)
```

Comparing every direct jump identifies the largest branch:

```asm
0040112f: cmp edx, 0x33
00401132: jmp 0x00401014
```

The `jmp rel32` instruction is five bytes long, so its following address is `0x401137`:

```text
0x401137 - 0x401014 = 0x123
```

The “great big leap” requested by the poem is therefore the hexadecimal distance `0x123`.

## 3. Automated Solution

The included solver disassembles the PE `.text` section with Capstone, calculates every direct jump displacement, and places the largest hexadecimal distance in the flag format:

```bash
python3 solve.py goingtoofaraway5.exe
```

Output:

```text
largest jump: 0x401132 -> 0x401014 (-0x123)
grodno{123}
```

## Flag

```text
grodno{123}
```

## Key Point

The meaningful data is not in the fake strings or normal runtime behavior. It is the relative jump distance described by the poem.
