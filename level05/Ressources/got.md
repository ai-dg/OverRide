# GOT and PLT (Global Offset Table / Procedure Linkage Table)

## What are they?

When a program uses shared libraries (like libc), the actual addresses of library functions are not known at compile time. The **GOT** and **PLT** work together to resolve these addresses at runtime.

- **PLT (Procedure Linkage Table)**: a set of small code stubs in the `.plt` section. When the program calls `exit()`, it actually calls the PLT stub for `exit`.
- **GOT (Global Offset Table)**: a table of pointers in the `.got.plt` section. Each PLT stub reads the real function address from the corresponding GOT entry and jumps there.

## How lazy binding works

On the first call to `exit()`:

```
1. Program calls exit@PLT
2. PLT stub reads GOT[exit] → initially points back to PLT (resolver)
3. Dynamic linker resolves real exit() address
4. GOT[exit] is updated with the real address
5. Jump to real exit()
```

On subsequent calls, GOT[exit] already contains the real address — no resolver needed.

## GOT overwrite attack

If the GOT is writable (no Full RELRO), an attacker who can write to arbitrary memory can replace a GOT entry with a different address. When the program next calls that function, it jumps to the attacker's target instead.

```
Before:  GOT[exit] → 0xf7e5eb70 (real exit)
After:   GOT[exit] → 0xffffd884 (shellcode address)

Program calls exit() → jumps to shellcode
```

## RELRO protection levels

| Level | GOT writable? | Impact |
|-------|--------------|--------|
| **No RELRO** | Yes | GOT fully writable |
| **Partial RELRO** | Yes (`.got.plt`) | GOT still writable, but `.got` is read-only |
| **Full RELRO** | No | All GOT entries resolved at load time, then made read-only |

## How to find GOT addresses

```bash
objdump -R ./binary | grep exit
readelf -r ./binary | grep exit
```

## In this project (Level05)

- `exit@GOT` is at `0x080497e0` (found with `objdump -R`)
- Partial RELRO → GOT is writable
- Format string `%hn` writes overwrite `exit@GOT` with shellcode address
- When `exit(0)` is called after `printf`, execution jumps to shellcode

## References

- PLT and GOT (Ian Lance Taylor): https://www.airs.com/blog/archives/38
- ELF Dynamic Linking: https://refspecs.linuxfoundation.org/ELF/zaux/Linux.Elf/node34.html
- RELRO explanation: https://www.redhat.com/en/blog/hardening-elf-binaries-using-relocation-read-only-relro
