# Level03 — Walkthrough

## Overview

The binary asks for a password (an integer). It XOR-decrypts a hidden string using a key derived from our input. If the decrypted string matches a target, it spawns a shell via `system()`. Our goal is to find the correct integer input.

---

## Step 1 — Analyze `main`

We start by disassembling `main` in GDB:

```
(gdb) disas main
```

Key observations:

- `srand(time(0))` seeds the random number generator (relevant only for the failure path).
- `scanf("%d", &input)` reads an integer from the user.
- It then calls `test(input, 0x1337d00d)`.

**Why this matters:** The second argument `0x1337d00d` (322424845 in decimal) is a hardcoded constant. Our input is the first argument. Both are passed to `test`, so we need to understand what `test` does with them.

---

## Step 2 — Analyze `test`

```
(gdb) disas test
```

Key observations:

- It computes `key = 0x1337d00d - input` (second arg minus first arg).
- If `key` is between 0 and 21 (inclusive), it enters a jump table (a `switch` statement) where every single case calls `decrypt(key)`.
- If `key > 21`, it calls `decrypt(rand())` instead — a random value we can't control.

**Why this matters:** All 22 switch cases (0–21) do the exact same thing: call `decrypt(key)`. So we just need to figure out which key value (0–21) produces the correct decryption. Once we know the key, we compute `input = 0x1337d00d - key`.

---

## Step 3 — Analyze `decrypt`

```
(gdb) disas decrypt
```

This is where the core logic lives. Here's what happens:

### 3a — The encrypted buffer

The function builds a 16-byte string on the stack:

```
0x757c7d51  0x67667360  0x7b66737e  0x33617c7d
```

Reading byte by byte (little-endian): `51 7d 7c 75 60 73 66 67 7e 73 66 7b 7d 7c 61 33`, followed by a null terminator.

### 3b — XOR decryption loop

The function loops through every byte of this buffer and XORs it with the key argument:

```c
for (i = 0; i < strlen(buffer); i++)
    buffer[i] ^= key;
```

### 3c — Comparison

After decryption, the result is compared (using `repz cmpsb`, which is essentially `strncmp`) against a reference string stored at address `0x80489c3`. This string is `"Congratulations!"` (17 characters including the null byte — matching the `0x11` count).

- If they match → `system("/bin/sh")` is called (we get a shell).
- If they don't match → it prints `"Nope"`.

**Why this matters:** We need to find the XOR key that turns the encrypted buffer into `"Congratulations!"`.

---

## Step 4 — Find the correct key

We XOR the first encrypted byte with the first expected byte:

```
encrypted[0] = 0x51 ('Q')
expected[0]  = 0x43 ('C')   # first char of "Congratulations!"

key = 0x51 ^ 0x43 = 0x12 = 18
```

We can verify with the second byte:

```
encrypted[1] = 0x7d
expected[1]  = 0x6f ('o')

0x7d ^ 0x12 = 0x6f  ✓
```

The correct key is **18**.

---

## Step 5 — Compute the password

Since `key = 0x1337d00d - input`, we solve for input:

```
input = 0x1337d00d - 18
input = 322424845 - 18
input = 322424827
```

---

## Step 6 — Exploit

```bash
level03@OverRide:~$ ./level03
***********************************
*               level03         **
***********************************
Password:322424827
$ cat /home/users/level04/.pass
```

This gives us the flag/password for level04.

---

## Summary of concepts used

| Concept | How it was used |
|---|---|
| **Reverse engineering** | Disassembling `main`, `test`, and `decrypt` in GDB to understand program flow |
| **Switch/jump table** | `test` uses a jump table for values 0–21, all leading to `decrypt(key)` |
| **XOR cipher** | `decrypt` XORs a hardcoded buffer with the key to produce a cleartext string |
| **Known-plaintext attack** | We know the expected output ("Congratulations!"), so we XOR it with the ciphertext to recover the key |
| **Simple arithmetic** | Once the key is known, computing `input = 0x1337d00d - key` gives us the password |