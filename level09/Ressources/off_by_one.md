# Off-by-One Error

## What is it?

An off-by-one error occurs when a loop or copy operation processes one element too many (or too few). In C, this typically means writing past the end of a buffer by exactly one byte — enough to corrupt adjacent data.

## The classic pattern

```c
char buf[40];
for (int i = 0; i <= 40; i++)   // BUG: should be i < 40
    buf[i] = src[i];
```

The loop runs for `i = 0, 1, ..., 40` — that's **41 iterations** for a 40-byte buffer. The 41st write (`buf[40]`) lands one byte past the buffer, overwriting whatever is stored there.

## Why one byte matters

In a structure where fields are adjacent in memory, one byte of overflow can corrupt the next field:

```
┌──────────────────┐
│ buffer[40]       │  offset 0x00 – 0x27
├──────────────────┤
│ length_field     │  offset 0x28 (4 bytes, little-endian)
└──────────────────┘
```

If the buffer overflow writes one byte at offset 0x28, it changes the **least significant byte** of `length_field` (little-endian). For example, `length_field` might go from `0x0000008c` (140) to `0x000000ff` (255).

If `length_field` is later used as a size for `strncpy` or `memcpy`, the corrupted value allows a much larger copy — turning a 1-byte overflow into a full buffer overflow.

## In this project (Level09)

- `set_username` copies with `i <= 0x28` (41 iterations) into a 40-byte `username` field
- The 41st byte overwrites the LSB of `msg_len` at `obj + 0xb4`
- Writing `\xff` changes `msg_len` from 140 to 255
- `strncpy(obj, msgbuf, 255)` then overflows past the structure, reaching saved RBP and saved RIP at offsets `0xc0` and `0xc8`
- RIP is overwritten with the address of `secret_backdoor` → shell

## The two-stage nature

Off-by-one errors are often **indirect**: the single byte doesn't directly overwrite a return address. Instead, it corrupts a **control value** (size, pointer, flag) that enables a larger overflow in a subsequent operation. This makes them harder to spot but equally dangerous.

## How to prevent it

- Use `<` instead of `<=` in loop bounds: `for (i = 0; i < sizeof(buf); i++)`
- Use `strncpy(dst, src, sizeof(dst) - 1)` and always null-terminate
- Prefer `snprintf` over manual byte-by-byte copies
- Use static analysis tools that detect off-by-one patterns

## References

- CWE-193 Off-by-one Error: https://cwe.mitre.org/data/definitions/193.html
- Off-by-one error (Wikipedia): https://en.wikipedia.org/wiki/Off-by-one_error
- OWASP Testing for Buffer Overflow: https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/13-Testing_for_Buffer_Overflow
