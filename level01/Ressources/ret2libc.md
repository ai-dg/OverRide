# Return-to-libc (ret2libc)

## What is it?

A ret2libc attack redirects a program's execution to existing functions in the C standard library (libc) instead of injecting shellcode. It bypasses NX (No-Execute) protection because no code is executed from the stack — only existing code in executable memory regions.

## How it works

When a function returns, the CPU pops the saved return address from the stack and jumps there. In a ret2libc attack, we overwrite this address with the address of a libc function (typically `system()`), and set up the stack so the function receives the right arguments.

### x86 (32-bit) calling convention

On i386, function arguments are passed on the stack. After the return address, the next value is the function's own return address, followed by its arguments:

```
┌─────────────────────┐
│ address of system()  │  ← overwritten saved EIP
├─────────────────────┤
│ address of exit()    │  ← system()'s return address
├─────────────────────┤
│ address of "/bin/sh" │  ← first argument to system()
└─────────────────────┘
```

When `ret` executes, EIP becomes `system()`. The `system` function reads its argument from the stack at the expected offset, finds `"/bin/sh"`, and spawns a shell.

## Key addresses to find (in GDB)

```
(gdb) p system          → address of system()
(gdb) p exit            → address of exit()
(gdb) find &system,+9999999,"/bin/sh"  → address of the string in libc
```

## Why it works even with NX

NX marks the stack as non-executable, so injected shellcode cannot run. But `system()` lives in libc's `.text` section, which is always executable. We're not running code from the stack — we're jumping to code that already exists.

## In this project (Level01)

- Stack is executable (RWE), but ret2libc is simpler and more reliable
- Offset to saved EIP: 80 bytes (buffer + alignment padding)
- `system()` at `0xf7e6aed0`, `exit()` at `0xf7e5eb70`, `"/bin/sh"` at `0xf7f897ec`

## Limitations

- Requires known libc addresses (defeated by ASLR unless leaked)
- Only works for simple function calls; complex logic needs ROP chains

## References

- Return-to-libc attack (Wikipedia): https://en.wikipedia.org/wiki/Return-to-libc_attack
- CWE-676 Use of Potentially Dangerous Function: https://cwe.mitre.org/data/definitions/676.html
- LiveOverflow — ret2libc: https://www.youtube.com/watch?v=m17mV24TgwY
