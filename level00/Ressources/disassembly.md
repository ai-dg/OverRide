# level00 — `main` (GDB)

```text
(gdb) disas main
Dump of assembler code for function main:
   0x08048494 <+0>:     push   %ebp
   ---> Save caller’s frame pointer on the stack (function prologue).

   0x08048495 <+1>:     mov    %esp,%ebp
   ---> Establish stack frame: %ebp points at saved %ebp / frame base.

   0x08048497 <+3>:     and    $0xfffffff0,%esp
   ---> Align %esp down to 16 bytes (ABI / SSE alignment).

   0x0804849a <+6>:     sub    $0x20,%esp
   ---> Allocate 32 bytes of stack locals (password int + padding / scanf args).

   0x0804849d <+9>:     movl   $0x80485f0,(%esp)
   ---> Put address of first banner string on stack as argument for puts().

   0x080484a4 <+16>:    call   0x8048390 <puts@plt>
   ---> Print first line of the “Level00” box.

   0x080484a9 <+21>:    movl   $0x8048614,(%esp)
   ---> Load second string pointer for puts().

   0x080484b0 <+28>:    call   0x8048390 <puts@plt>
   ---> Print second banner line.

   0x080484b5 <+33>:    movl   $0x80485f0,(%esp)
   ---> Reload first banner string (repeat top border).

   0x080484bc <+40>:    call   0x8048390 <puts@plt>
   ---> Print third line (same as first line of the box).

   0x080484c1 <+45>:    mov    $0x804862c,%eax
   ---> Load address of "Password:" format / string (passed to printf).

   0x080484c6 <+50>:    mov    %eax,(%esp)
   ---> Place format string pointer as first (and only) printf argument.

   0x080484c9 <+53>:    call   0x8048380 <printf@plt>
   ---> Prompt user (no newline in string — same as printf("Password:")).

   0x080484ce <+58>:    mov    $0x8048636,%eax
   ---> Load scanf format string address (typically "%d").

   0x080484d3 <+63>:    lea    0x1c(%esp),%edx
   ---> Compute address of local int at esp+0x1c — destination for scanf.

   0x080484d7 <+67>:    mov    %edx,0x4(%esp)
   ---> Second arg to scanf: pointer to scanned integer (stack layout for variadic ABI).

   0x080484db <+71>:    mov    %eax,(%esp)
   ---> First arg: format string "%d".

   0x080484de <+74>:    call   0x80483d0 <__isoc99_scanf@plt>
   ---> Read one signed decimal int into the local buffer (expected password).

   0x080484e3 <+79>:    mov    0x1c(%esp),%eax
   ---> Load scanned value into %eax for comparison.

   0x080484e7 <+83>:    cmp    $0x149c,%eax
   ---> Compare input with hardcoded constant 0x149c (5276 decimal).

   0x080484ec <+88>:    jne    0x804850d <main+121>
   ---> If not equal, skip success path — jump to “Invalid Password”.

   0x080484ee <+90>:    movl   $0x8048639,(%esp)
   ---> Success: pointer to string "\nAuthenticated!" (or similar).

   0x080484f5 <+97>:    call   0x8048390 <puts@plt>
   ---> Print authentication success message.

   0x080484fa <+102>:   movl   $0x8048649,(%esp)
   ---> Load pointer to "/bin/sh" (or command string) for system().

   0x08048501 <+109>:   call   0x80483a0 <system@plt>
   ---> Spawn shell — reward path when password matches.

   0x08048506 <+114>:   mov    $0x0,%eax
   ---> Set return value 0 (success) in %eax.

   0x0804850b <+119>:   jmp    0x804851e <main+138>
   ---> Skip failure branch; go to function epilogue.

   0x0804850d <+121>:   movl   $0x8048651,(%esp)
   ---> Failure: pointer to "\nInvalid Password!" string.

   0x08048514 <+128>:   call   0x8048390 <puts@plt>
   ---> Print failure message.

   0x08048519 <+133>:   mov    $0x1,%eax
   ---> Return value 1 (failure) from main.

   0x0804851e <+138>:   leave
   ---> Tear down frame: mov %ebp,%esp; pop %ebp.

   0x0804851f <+139>:   ret
   ---> Return to libc start / exit with status in %eax.

End of assembler dump.
```

**Exploitation note:** The check is a plain constant compare — no stack corruption; the “exploit” is discovering `0x149c` (static analysis, test input, or disassembly).
