# Junior Crypt 2026 CTF - `Clockwork Vault` Writeup

- **Author:** Efe Sahinbas
- **Category:** Pwn
- **Difficulty:** Medium
- **File:** `clockwork_vault`

## Summary

The program manages a global mechanism array but checks only the upper bound of a signed index. Negative indices expose the `service_cookie` and the active service slot stored immediately before the array.

## Analysis

The binary has NX, PIE, and Full RELRO. Symbols reveal `slots`, `service_cookie`, `idle_cycle`, `trigger_alarm`, and `open_vault`.

Both inspect and retune effectively perform:

```c
if (index >= SLOT_COUNT)
    reject();
// No index < 0 check.
slot = &slots[index];
```

Index `-2` leaks the pointer-encoding cookie. Index `-1` exposes and modifies the slot used by the service cycle. Actions are encoded as:

```text
encoded_action = service_cookie XOR function_address
```

Because the remote build differed from the supplied binary, the exploit decoded the existing remote idle action instead of assuming the local PIE layout:

```text
idle_cycle = leaked_encoded_action XOR service_cookie
```

Redirecting the slot to `trigger_alarm` first confirmed the write primitive. The exploit then encoded the nearby remote `open_vault` address, wrote it through index `-1`, supplied the required setting magic, and ran the service cycle. The indirect call reached `open_vault()` and printed the flag.

## Flag

```text
grodno{7e167a02-b1f1-409c-976d-5717470a22d6}
```

## Root Cause

A missing lower-bound check on a signed array index enables an out-of-bounds leak and function-pointer overwrite.
