#!/usr/bin/env python3

from pathlib import Path


MOD = 1 << 32
A = 1664525
C = 1013904223


def keystream(seed, length):
    state = seed & 0xFFFFF
    out = bytearray()
    for _ in range(length):
        state = (A * state + C) % MOD
        out.append((state >> 24) & 0xFF)
    return bytes(out)


def xor_bytes(left, right):
    return bytes(a ^ b for a, b in zip(left, right))


base = Path(__file__).resolve().parent
ciphertext = bytes.fromhex((base / "ciphertext.txt").read_text().strip())

for seed in range(1 << 20):
    plaintext = xor_bytes(ciphertext, keystream(seed, len(ciphertext)))
    if b"grodno{" in plaintext:
        print(f"seed: {seed}")
        print(plaintext.decode())
        break
