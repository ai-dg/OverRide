# Level06 — Walkthrough

## 1. Discovering what we have

When we log in as `level06`, we find a binary in the home directory:

```
level06@OverRide:~$ ls -l
-rwsr-s---+ 1 level07 users 7907 Sep 10  2016 level06
```

The binary has the **SUID bit** set (`rws`). This means when we run it, it executes with the permissions of `level07` — not `level06`. If we can make the program spawn a shell, that shell will run as `level07`, letting us read the next level's password.

---

## 2. Running the binary to understand its behavior

```
level06@OverRide:~$ ./level06
***********************************
*               level06           *
***********************************
-> Enter Login: hello
***********************************
***** NEW ACCOUNT DETECTED ********
***********************************
-> Enter Serial: 12345
```

The program asks for two things:
- A **login** (a string)
- A **serial number** (an integer)

If the serial doesn't match what the program expects for that login, nothing happens (it just exits). We need to figure out what serial the program expects.

---

## 3. Disassembling `main` with GDB

We open the binary in GDB to read its assembly code:

```
level06@OverRide:~$ gdb ./level06
(gdb) disas main
```

From the disassembly, we identify the key flow:

1. The program prints banners using `puts`.
2. It reads the login string with `fgets(buffer, 32, stdin)` — so the login is at most 32 characters.
3. It reads the serial number with `scanf("%d", &serial)`.
4. It calls `auth(login, serial)`.
5. **If `auth` returns 0** → it calls `system("/bin/sh")`, giving us a shell.
6. If `auth` returns anything else → the program exits with no shell.

The critical question: **what does `auth` check?**

---

## 4. Disassembling `auth`

```
(gdb) disas auth
```

By reading the assembly instruction by instruction, we can reconstruct the C code that `auth` implements. Here is what it does:

### Step A — Strip the newline and check length

```c
login[strcspn(login, "\n")] = '\0';  // remove trailing newline
int len = strnlen(login, 32);
if (len <= 5) return 1;              // login must be longer than 5 characters
```

- `strcspn(login, "\n")` finds the position of the first newline character. The program replaces it with a null byte to clean up the input from `fgets`.
- If the login is 5 characters or fewer, the function immediately returns 1 (failure).

### Step B — Anti-debugging check with `ptrace`

```c
if (ptrace(PTRACE_TRACEME, 0, 1, 0) == -1)
    return 1;
```

`ptrace` is a system call used by debuggers like GDB. When a program calls `ptrace(PTRACE_TRACEME)`, it asks the OS to let a parent process trace it. But **if a debugger is already attached** (like GDB), this call fails and returns `-1`.

This is an **anti-debugging technique**: if someone is running the program under GDB, `ptrace` fails and the function returns 1 (authentication denied). This prevents us from simply stepping through the code in GDB to bypass the check.

**Important consequence**: we cannot just set a breakpoint and change the return value inside GDB, because the `ptrace` check will make it fail. We need to understand the algorithm and compute the correct serial ourselves.

### Step C — Computing the expected serial (the hash)

```c
int hash = (login[3] ^ 0x1337) + 0x5eeded;
```

- `login[3]` is the 4th character of the login (index starts at 0).
- `^` is the XOR bitwise operation. XOR flips bits: each bit of the result is 1 if the corresponding bits of the operands are different, 0 if they're the same.
- `0x1337` and `0x5eeded` are hexadecimal constants.
- This creates an initial hash value from just one character of the login.

### Step D — The loop that updates the hash

```c
for (int i = 0; i < len; i++) {
    if (login[i] <= 31) return 1;  // reject control characters
    int c = login[i] ^ hash;
    hash += c % 1337;
}
```

For each character in the login:
1. **Control character check**: if the character's ASCII value is 31 or less (these are non-printable control characters like tab, newline, etc.), return 1 (fail).
2. **XOR the character with the current hash** to produce a value `c`.
3. **Take `c % 1337`** (the remainder when dividing by 1337).
4. **Add that remainder to the hash**.

The number `1337` (which is `0x539` in hex) is just an arbitrary constant chosen by the challenge creators.

### Step E — Final comparison

```c
return (serial == hash) ? 0 : 1;
```

After the loop, the computed `hash` is compared to the serial number we entered. If they match, the function returns 0 (success), and `main` gives us a shell.

---

## 5. Computing the correct serial

Now that we understand the algorithm, we can pick any login longer than 5 characters and compute the expected serial. We use Python, which is available on the VM:

```
level06@OverRide:~$ python -c '
login = "aaaaaa"
h = (ord(login[3]) ^ 0x1337) + 0x5eeded
for c in login:
    v = ord(c) ^ h
    h += v % 1337
print h
'
```

**What this script does:**
- `ord(c)` converts a character to its ASCII integer value. For `'a'`, that's 97.
- It follows exactly the same algorithm the binary uses.
- It prints the final hash value, which is the serial we need.

The output is: **6231562**

---

## 6. Exploiting the binary

Now we run the binary with our chosen login and computed serial:

```
level06@OverRide:~$ ./level06
***********************************
*               level06           *
***********************************
-> Enter Login: aaaaaa
***********************************
***** NEW ACCOUNT DETECTED ********
***********************************
-> Enter Serial: 6231562
Authenticated!
$
```

We get a shell running as `level07`. We can now read the password:

```
$ cat /home/users/level07/.pass
```

---

## 7. Summary

| Step | What we did | Why |
|------|-------------|-----|
| 1 | Ran the binary | Understand what inputs it expects |
| 2 | Disassembled `main` | Found that `auth` returning 0 gives a shell |
| 3 | Disassembled `auth` | Reverse-engineered the serial computation algorithm |
| 4 | Noticed the `ptrace` check | Understood we can't bypass it with GDB — we must compute the serial |
| 5 | Wrote a Python script | Replicated the algorithm to compute the correct serial for our login |
| 6 | Entered login + serial | Got authenticated and spawned a shell as `level07` |

The core vulnerability is that the serial validation algorithm is entirely **deterministic and reversible** — knowing the login is enough to compute the valid serial. There is no secret key or external data involved.