#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path

from Crypto.Util.number import long_to_bytes


def trim(poly):
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def monic(poly, modulus):
    poly = trim([x % modulus for x in poly])
    inv = pow(poly[-1], -1, modulus)
    return [(x * inv) % modulus for x in poly]


def divmod_poly(left, right, modulus):
    left = trim(left[:])
    right = trim(right[:])
    quotient = [0] * max(1, len(left) - len(right) + 1)
    inv_lc = pow(right[-1], -1, modulus)

    while len(left) >= len(right) and left != [0]:
        degree = len(left) - len(right)
        coeff = left[-1] * inv_lc % modulus
        quotient[degree] = coeff
        for i, value in enumerate(right):
            left[i + degree] = (left[i + degree] - coeff * value) % modulus
        trim(left)

    return trim(quotient), trim(left)


def gcd_poly(left, right, modulus):
    left = trim([x % modulus for x in left])
    right = trim([x % modulus for x in right])

    while right != [0]:
        _, remainder = divmod_poly(left, right, modulus)
        left, right = right, remainder

    return monic(left, modulus)


base = Path(__file__).resolve().parent
data = json.loads((base / "ciphertexts.json").read_text())

modulus_line = subprocess.check_output(
    ["openssl", "rsa", "-pubin", "-in", str(base / "public.pem"), "-modulus", "-noout"],
    text=True,
).strip()
n = int(modulus_line.split("=", 1)[1], 16)

c1 = int(data["c1"])
c2 = int(data["c2"])
a = int(data["a"])
b = int(data["b"])

f = [(-c1) % n, 0, 0, 1]
g = [(b**3 - c2) % n, (3 * a * b * b) % n, (3 * a * a * b) % n, pow(a, 3, n)]

divisor = gcd_poly(f, g, n)
message = (-divisor[0]) % n

print(long_to_bytes(message).decode())
