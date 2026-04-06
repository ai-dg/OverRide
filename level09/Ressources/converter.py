#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Usage (depuis level09/) :
  python2 Ressources/converter.py 0xADDR_POP_RDI 0xADDR_BIN_SH 0xADDR_SYSTEM

Affiche les trois lignes a coller dans Ressources/payload.py (POP_RDI_RET, BIN_SH, SYSTEM).
Pas d'execution automatique du binaire : valeurs issues de GDB / ROPgadget sur la VM.
"""

import sys


def main():
    if len(sys.argv) != 4:
        sys.stderr.write(
            "Usage: python2 Ressources/converter.py <POP_RDI_RET> <BIN_SH> <SYSTEM>\n"
            "Exemple: python2 Ressources/converter.py 0x40123a 0x402000 0x401040\n"
        )
        sys.exit(1)

    def parse_hex(s):
        s = s.lower().strip()
        if s.startswith("0x"):
            s = s[2:]
        return int(s, 16)

    a, b, c = [parse_hex(x) for x in sys.argv[1:4]]
    print("POP_RDI_RET = " + hex(a))
    print("BIN_SH      = " + hex(b))
    print("SYSTEM      = " + hex(c))
    print("")
    print("# Puis : ( python2 Ressources/payload.py ; cat ) | ./level09")


if __name__ == "__main__":
    main()
