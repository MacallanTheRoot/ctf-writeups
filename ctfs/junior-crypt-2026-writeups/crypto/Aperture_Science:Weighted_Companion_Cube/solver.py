#!/usr/bin/env python3

import json
from pathlib import Path


def xor_bytes(left, right):
    return bytes(a ^ b for a, b in zip(left, right))


def record(item, status, sector, memo):
    return (
        "[Aperture Archive]\n"
        f"item={item:<18}\n"
        f"status={status:<12}\n"
        f"sector={sector:<12}\n"
        f"memo={memo:<64}\n"
    ).encode()


base = Path(__file__).resolve().parent
known = json.loads((base / "known_archives.json").read_text())
secret = bytes.fromhex((base / "secret_archive.hex").read_text().strip())

known_plaintext = record(
    "companion cube",
    "issued",
    "alpha-17",
    "incineration queue delayed until morale stabilizes",
)
known_ciphertext = bytes.fromhex(known[0]["ciphertext_hex"])

keystream = xor_bytes(known_plaintext, known_ciphertext)
plaintext = xor_bytes(secret, keystream)

print(plaintext.decode())
