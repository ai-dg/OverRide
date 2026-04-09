# OverRide

A binary exploitation project following RainFall. Each level is a setuid ELF binary with a deliberate vulnerability — exploit it to read the next level's password.

---

## Key Concepts

### Hardcoded Credentials
Secrets embedded directly in the binary (constants in `cmp` instructions, strings in `.rodata`) are trivially recoverable via disassembly or `strings`. No memory corruption needed — the flaw is purely logical.
> Level00, Level01, Level06

### Stack Buffer Overflow
When a fixed-size stack buffer is written past its bounds (via `gets`, `fgets` with a larger size, etc.), the attacker controls saved EBP and EIP. Classic payloads: **ret2libc** (chain `system` + `exit` + `"/bin/sh"`) or **ROP** when the stack is non-executable.
> Level01, Level04

### Format String
Passing attacker-controlled input directly to `printf` as the format argument allows arbitrary reads (`%x`, `%p`) and writes (`%n`) anywhere in memory. Common targets: a password sitting on the stack, or a GOT entry to redirect execution.
> Level02, Level05

### Cipher / Logic Reversal
Some levels protect access with a custom algorithm (XOR cipher, hash function). Since the algorithm and its constants are in the binary, an attacker can reverse-engineer it offline and compute the correct input without any memory corruption.
> Level03, Level06

### Out-of-Bounds Array Write
When an array index is not bounds-checked, large indices reach memory beyond the array — including the saved return address on the stack. Combined with integer overflow on the index computation, this enables arbitrary relative writes.
> Level07

### Path Traversal / Symlink Abuse
A setuid binary that opens a file supplied by the user can be tricked via a symlink: create a link with an innocuous name pointing to a privileged file. The binary follows the link with elevated rights, leaking content the attacker cannot read directly.
> Level08

### Off-by-One
A loop bounded with `<=` instead of `<` writes one byte past the end of a buffer. That single byte lands in a neighboring field (e.g. a length), corrupting it enough to turn a later bounded copy into an unbounded overflow — overwriting saved RIP and hijacking control flow.
> Level09

---

## Protections Encountered

| Protection | Effect when absent |
|---|---|
| **Stack canary** | Overflow reaches saved EIP undetected |
| **NX / DEP** | Stack is executable — shellcode is viable |
| **PIE** | Binary loads at a fixed address — no ASLR on the text segment |
| **RELRO (partial)** | GOT entries are writable — format string can overwrite them |
| **ptrace anti-debug** | Prevents attaching a debugger; work around by reimplementing the check offline |
