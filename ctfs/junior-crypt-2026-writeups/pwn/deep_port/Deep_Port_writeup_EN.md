# Junior Crypt 2026 CTF - `Deep Port` Writeup

- **Author:** Efe Sahinbas
- **Category:** Pwn
- **Difficulty:** Hard
- **File:** `deep_port`

## Summary

Releasing a shipment frees its manifest but leaves the slot pointer and size intact. The stale slot remains viewable and editable, enabling address leaks, safe-linking recovery, and tcache poisoning.

## Analysis

The view operation leaks both the stale manifest pointer and a route function pointer. These provide the heap position required for safe-linking and a remote text reference.

Two chunks in the same size class are freed. The dangling chunk's tcache forward pointer is replaced using glibc's safe-linking formula:

```text
encoded_next = target XOR (freed_chunk_address >> 12)
```

Keeping two entries in the bin is important: with a tcache count of one, the poisoned head is ignored after the first allocation reduces the count to zero. With two entries, the second allocation returns the chosen target.

The reliable remote target was the dispatch hook located relative to the leaked stale manifest:

```text
target = manifest_pointer - 0x30
print_flag = standby + 0x20
```

The poisoned allocation overlapped `harbor->dispatch_hook`. Writing the calculated remote `print_flag` address there and selecting dispatch printed the flag.

## Flag

```text
grodno{03786281-13d3-41a1-bcbd-e2bc99b9770f}
```

## Root Cause

Shipment metadata is not cleared after free, leaving an editable use-after-free that permits tcache freelist poisoning.
