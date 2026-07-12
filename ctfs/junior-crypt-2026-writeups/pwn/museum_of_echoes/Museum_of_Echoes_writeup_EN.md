# Junior Crypt 2026 CTF - `Museum of Echoes` Writeup

- **Author:** Efe Sahinbas
- **Category:** Pwn
- **Difficulty:** Hard
- **File:** `museum_of_echoes`

## Summary

A small `whisper` exhibit can be reclassified as the larger `chorus` type without reallocating its heap object. Rewriting it as a chorus overflows the original chunk and corrupts the adjacent exhibit's metadata and routine pointer.

## Analysis

Full RELRO, NX, PIE, and stack canaries are enabled. Debug symbols expose the two object layouts: a chorus needs more storage because it contains both an intro and a refrain.

The exploit performs the following steps:

1. Allocate two adjacent whisper exhibits.
2. Reclassify the first object as a chorus.
3. Use the chorus rewrite operation to overflow into the second chunk.
4. Preserve a valid chunk layout and set the second object's marker to `0x4543484f` (`ECHO`).
5. Replace its perform pointer with `grand_finale`.
6. Perform the corrupted second exhibit.

The remote executable was not byte-identical to the attachment. Leaks gave `whisper_perform = 0x401296` and `chorus_perform = 0x4012cb`; a narrow probe of valid nearby function entries identified `grand_finale = 0x401308`.

Performing the corrupted exhibit transferred control to `grand_finale()`, which printed `flag.txt`.

## Flag

```text
grodno{a5b7cb45-ac23-436a-ae13-851e6f90dcfb}
```

## Root Cause

Reclassification changes the logical type without resizing the allocation, producing a type-confusion heap overflow.
