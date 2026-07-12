#!/usr/bin/env python3
"""Find the largest relative jump in A Great Big Leap."""

import argparse
import pefile
from capstone import CS_ARCH_X86, CS_MODE_32, Cs
from capstone.x86_const import X86_OP_IMM


def solve(path):
    pe = pefile.PE(path)
    text = next(section for section in pe.sections if section.Name.rstrip(b"\0") == b".text")
    base = pe.OPTIONAL_HEADER.ImageBase + text.VirtualAddress
    disassembler = Cs(CS_ARCH_X86, CS_MODE_32)
    disassembler.detail = True

    jumps = []
    for instruction in disassembler.disasm(text.get_data(), base):
        if instruction.mnemonic.startswith("j") and instruction.operands:
            operand = instruction.operands[0]
            if operand.type == X86_OP_IMM:
                displacement = operand.imm - (instruction.address + instruction.size)
                jumps.append((abs(displacement), displacement, instruction))

    distance, displacement, instruction = max(jumps, key=lambda item: item[0])
    print(
        f"largest jump: {instruction.address:#x} -> "
        f"{instruction.operands[0].imm:#x} ({displacement:+#x})"
    )
    print(f"grodno{{{distance:x}}}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", help="goingtoofaraway5.exe")
    args = parser.parse_args()
    solve(args.binary)
