# Format String Vulnerability

## What is it?

A format string vulnerability occurs when user-controlled input is passed directly as the format string argument to `printf`, `fprintf`, `sprintf`, or similar functions. Instead of `printf("%s", user_input)`, the code does `printf(user_input)`.

## Why it's dangerous

`printf` interprets format specifiers (`%x`, `%p`, `%s`, `%n`) in its first argument. If the attacker controls that argument, they can:

1. **Read memory** — `%p` or `%x` prints values from the stack (or registers on x86-64)
2. **Write memory** — `%n` writes the number of characters printed so far to an address on the stack
3. **Arbitrary read/write** — by placing addresses in the format string and using `%N$p` or `%N$n` to reference specific stack positions

## Key specifiers

| Specifier | Action | Size |
|-----------|--------|------|
| `%p` | Print pointer (read) | 4 or 8 bytes |
| `%x` | Print hex (read) | 4 bytes |
| `%n` | Write char count | 4 bytes |
| `%hn` | Write char count | 2 bytes (short) |
| `%hhn` | Write char count | 1 byte |
| `%N$p` | Read the Nth argument | direct access |

## x86-64 specifics

On x86-64, the first 5 `printf` arguments come from registers (`rsi`, `rdx`, `rcx`, `r8`, `r9`). Arguments 6+ come from the stack. So the format string buffer typically appears at offset 6 or higher.

## In this project (Level02)

- `printf(username)` on the failure path leaks stack data
- The file password (41 bytes from `.pass`) is on the stack before `printf` is called
- Using `%22$p` through `%26$p` reads the password directly as 5 × 8-byte hex values
- Decoding little-endian hex to ASCII recovers the plaintext password

## How to fix it

- Always use `printf("%s", user_input)` instead of `printf(user_input)`
- Use compiler warnings: `-Wformat -Wformat-security`
- Enable FORTIFY_SOURCE: `-D_FORTIFY_SOURCE=2`

## References

- OWASP Format String Attack: https://owasp.org/www-community/attacks/Format_string_attack
- CWE-134 Use of Externally-Controlled Format String: https://cwe.mitre.org/data/definitions/134.html
- Exploiting Format String Vulnerabilities (scut/team teso): https://cs155.stanford.edu/papers/formatstring-1.2.pdf
