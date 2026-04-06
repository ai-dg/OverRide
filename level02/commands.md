# Level02 — commands

## Interpreter on the VM

```bash
which python python2 python3 2>/dev/null
```

Use **`python` or `python2`** if `python3` is missing (same as level01).

---

## Format string — two stdin lines

The program reads:

1. **Username** → `line_user` (becomes the **format string** on the failing branch: `printf(line_user)`).
2. **Password** → compared with `.pass`; must be **wrong** to hit `printf(line_user)`.

So: **line 1** = payload, **line 2** = anything except the real password (e.g. `wrong`).

---

## Recon — leak stack pointers (Python 2)

```bash
( python -c "import sys; sys.stdout.write('%p.'*30+'\n'+'wrong\n')" ) | ./level02
```

### How to know this step **worked**

You should see:

- A long line of **hex values** separated by dots, e.g. `0x7fffffffe500.(nil).0x77...`
- The line ends with **` does not have access!`**

That **is success** for this **recon** command. The program **must** take the **wrong password** branch so `printf(line_user)` runs — so you **always** get the *“does not have access!”* suffix. You do **not** get a shell from `%p` alone.

Values like **`0x70252e70252e7025`** at the end are the stack interpreting raw bytes of your **`%p.`** pattern (ASCII), not a failure.

**If** you see no hex leak and only the banner → pipe / Python issue. **If** you see the leak → move on to GDB: find argument index for **`%<pos>$p`**, then build **`%n`** / GOT (final command is different from this one).

Purpose: map stack slots (then refine to **`%n`** / GOT overwrite per your GDB notes).

**Python 3** (if installed):

```bash
( python3 -c "import sys; sys.stdout.buffer.write(b'%p.'*30+b'\n'+b'wrong\n')" ) | ./level02
```

---

## Common mistake

- **`python3` not installed** → subshell prints nothing useful; pipe is empty or wrong → exploit fails.
- **Literal `<FORMAT_STRING>`** in the command → that text is sent as the username, not a real format payload.

---

## Password file path (binary)

The binary opens **`/home/users/level03/.pass`**. If `fopen` fails locally, you see `ERROR: failed to open password file` — run on the VM as **`level02`** where that path exists.

---

## After recon — you are **not** done yet

The `%p` dump proves **`printf` reads the stack**; it does **not** give a shell. You still need:

1. **Find the argument index** of your buffer (where the start of `line_user` appears as a `printf` vararg). On **x86-64**, the first args are often passed in **registers** (`rdi, rsi, rdx, …`); the format string itself is not always “at `%1$p`”. Use probes:
   ```bash
   ( python -c 'import sys; sys.stdout.write("AAAA%6$p\nwrong\n")' ) | ./level02
   ```
   Change **`6`** to `7`, `8`, … until you see **`0x41414141`** (or `41414141`). That index is **`POS`** for **`%POS$p` / `%POS$n`**. (Outer **single quotes** for `bash` so **`$p`** is not expanded by the shell.)

2. **Pick a GOT slot** (from `readelf -r ./level02` on the **VM** — addresses can differ from another machine). Typical targets on this binary include **`exit@GOT`** or **`printf@GOT`** (see **Jump slot** column).

3. **Write** the address you want (e.g. **`system`** from libc) with **`%n` / `%hn` / `%hhn`**, often in **several steps** for a full 64-bit pointer, and align **addresses** in the username buffer so **`%k$`** points at them.

4. **Reliable libc base** if ASLR is on: leak a libc pointer with **`%p`**, subtract offset from GDB, then compute **`system`** and **`/bin/sh`**.

5. **Keep the second line wrong** (`wrong` or anything ≠ real `.pass`) so execution always reaches **`printf(line_user)`**.

Record the **final** one-liner (with **`POS`**, GOT addresses, libc values) here once measured on the **evaluation VM**.

---

## Final exploit (placeholder)

After GDB: build the username line with **`%<k>$n`**, padding, and **8-byte little-endian** addresses — `level02` is **x86-64**. Put the exact **`python`** command with **numeric** values in this section.
