# Junior Crypt 2026 CTF - `House of Mirage` Writeup

- **Author:** Efe Sahinbas
- **Category:** Pwn
- **Difficulty:** Medium
- **File:** `house_of_mirage`

## Summary

The archive thread scrubs an expired session and places its chunk on an internal free list, but it never removes the pointer from the active session array. When a sink reuses that chunk, the stale session API can overwrite the live sink object.

## Analysis

The stripped C++ PIE has Full RELRO, NX, and stack canaries. Session and sink objects are both `0x60` bytes. In the supplied binary, the hidden replay routine is at PIE offset `0x3970` and the regular session table is at `0x6030`.

The exploitation chain is:

```text
create session
-> arm expiry
-> archive puts its chunk on the free list
-> create sink reusing that chunk
-> overwrite the sink through stale session profile import
-> flush through a fake vtable into the replay routine
```

After reuse, showing the stale session interprets the sink's real function-table pointer as a serial number, providing a PIE leak. A fake table is then placed inside the controlled sink and its first entry is set to `PIE + 0x3970`.

The remote archive thread scrubbed reused chunks on a short interval. Sending `create sink -> arm stale session -> show stale session` in a single TCP burst won the race. Profile import then corrupted the sink, and flush dispatched through the fake table to the hidden replay routine.

## Flag

```text
grodno{51154113-985a-4f07-9db7-aba34670946c}
```

## Root Cause

Expiry leaves an active dangling pointer. Reallocation turns that use-after-free into a cross-type object overwrite and controlled indirect call.
