# Buffer Overflow (Stack)

## What is it?

A stack buffer overflow occurs when a program writes more data into a stack-allocated buffer than it can hold. The excess data overwrites adjacent memory — typically the saved frame pointer (EBP/RBP) and the saved return address (EIP/RIP).

## How it works

On x86, when a function is called, the CPU pushes the return address onto the stack. Local variables (buffers) are allocated below it:

```
High addresses
┌─────────────────────┐
│ saved EIP (ret addr) │  ← overwrite target
├─────────────────────┤
│ saved EBP            │
├─────────────────────┤
│ local buffer[N]      │  ← write starts here
├─────────────────────┤
│ ...                  │
└─────────────────────┘
Low addresses
```

If `fgets(buffer, size, stdin)` reads more bytes than `buffer` can hold, the extra bytes overwrite saved EBP and then saved EIP. By controlling EIP, the attacker controls where the program jumps when the function returns.

## How to spot it

- `fgets`, `gets`, `read`, `scanf("%s")`, `strcpy` writing into a fixed-size stack buffer
- The read size exceeds the buffer size (e.g., `fgets(buf, 100, stdin)` into a 64-byte buffer)
- No stack canary protection (`checksec` shows "No canary found")

## In this project (Level01)

- `fgets(pass, 0x64, stdin)` reads 100 bytes into a 64-byte buffer at `esp+0x1c`
- The overflow reaches saved EIP after 80 bytes (including stack alignment padding)
- Combined with ret2libc to redirect execution to `system("/bin/sh")`

## How to fix it

- Use bounded reads: ensure the size argument to `fgets`/`read` never exceeds the buffer size
- Enable stack canaries (`-fstack-protector`)
- Enable ASLR and NX to make exploitation harder

## References

- OWASP Buffer Overflow: https://owasp.org/www-community/vulnerabilities/Buffer_Overflow
- CWE-121 Stack-based Buffer Overflow: https://cwe.mitre.org/data/definitions/121.html
- Smashing the Stack for Fun and Profit (Aleph One): http://phrack.org/issues/49/14.html
