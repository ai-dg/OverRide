# level03 — `main` and `test`

## `main`

```text
(gdb) disas main
   0x0804885a <+0>:     push   %ebp
   ---> Prologue (32-bit).

   0x0804885b <+1>:     mov    %esp,%ebp
   ---> Frame pointer.

   0x0804885d <+3>:     and    $0xfffffff0,%esp
   ---> Align stack to 16 bytes.

   0x08048860 <+6>:     sub    $0x20,%esp
   ---> Reserve space for scanf argument + padding.

   0x08048863 <+9>:     push   %eax
   0x08048864 <+10>:    xor    %eax,%eax
   0x08048866 <+12>:    je     0x804886b <main+17>
   0x08048868 <+14>:    add    $0x4,%esp
   0x0804886b <+17>:    pop    %eax
   ---> Stack-alignment / stack-protector scratch (compiler stub around main body).

   0x0804886c <+18>:    movl   $0x0,(%esp)
   ---> Argument to time(): NULL → calendar time.

   0x08048873 <+25>:    call   0x80484b0 <time@plt>
   ---> time(NULL) for PRNG seed.

   0x08048878 <+30>:    mov    %eax,(%esp)
   ---> Pass time return value as seed.

   0x0804887b <+33>:    call   0x8048500 <srand@plt>
   ---> srand(seed) — used inside test() default path.

   0x08048880 <+38>:    movl   $0x8048a48,(%esp)
   ... puts ×3
   ---> Banner lines for “level03”.

   0x080488a4 <+74>:    mov    $0x8048a7b,%eax
   0x080488a9 <+79>:    mov    %eax,(%esp)
   0x080488ac <+82>:    call   0x8048480 <printf@plt>
   ---> printf("Password:") without newline.

   0x080488b1 <+87>:    mov    $0x8048a85,%eax
   ---> Address of "%u" format string.

   0x080488b6 <+92>:    lea    0x1c(%esp),%edx
   ---> Pointer to unsigned int local (scanf output).

   0x080488ba <+96>:    mov    %edx,0x4(%esp)
   ---> Second arg: &input.

   0x080488be <+100>:   mov    %eax,(%esp)
   ---> First arg: "%u".

   0x080488c1 <+103>:   call   0x8048530 <__isoc99_scanf@plt>
   ---> Read one unsigned int (typed password).

   0x080488c6 <+108>:   mov    0x1c(%esp),%eax
   ---> Load scanned value.

   0x080488ca <+112>:   movl   $0x1337d00d,0x4(%esp)
   ---> Second argument to test(): constant 0x1337d00d (second operand of subtraction in test).

   0x080488d2 <+120>:   mov    %eax,(%esp)
   ---> First argument: user input.

   0x080488d5 <+123>:   call   0x8048747 <test>
   ---> test(input, 0x1337d00d) — difference selects jump table case or rand path.

   0x080488da <+128>:   mov    $0x0,%eax
   ---> Return 0 from main.

   0x080488df <+133>:   leave
   0x080488e0 <+134>:   ret
   ---> Epilogue.

End of assembler dump.
```

## `test` (outline)

```text
08048747 <test>:
 8048747: 55                    push   %ebp
 8048748: 89 e5                 mov    %esp,%ebp
 804874a: 83 ec 28              sub    $0x28,%esp
 ---> Prologue; locals hold d = second_arg - first_arg.

 804874d: 8b 45 08              mov    0x8(%ebp),%eax
 8048750: 8b 55 0c              mov    0xc(%ebp),%edx
 ---> Load parameters (a, b).

 8048753: 89 d1                 mov    %edx,%ecx
 8048755: 29 c1                 sub    %eax,%ecx
 8048757: 89 c8                 mov    %ecx,%eax
 ---> d = b - a (unsigned subtract in C).

 8048759: 89 45 f4              mov    %eax,-0xc(%ebp)
 ---> Store d on stack.

 804875c: 83 7d f4 15           cmpl   $0x15,-0xc(%ebp)
 8048760: 0f 87 e4 00 00 00     ja     804884a <test+0x103>
 ---> If d > 21 (0x15), fall through to **rand + decrypt(rand)** “default” path.

 8048766: 8b 45 f4              mov    -0xc(%ebp),%eax
 8048769: c1 e0 02              shl    $0x2,%eax
 804876c: 05 f0 89 04 08        add    $0x80489f0,%eax
 8048771: 8b 00                 mov    (%eax),%eax
 8048773: ff e0                 jmp    *%eax
 ---> **Indirect jump**: jump table at 0x80489f0 indexed by d (0..21) → one case per dword.

 8048775 … 8048848:  (repeated pattern)
   mov    -0xc(%ebp),%eax
   mov    %eax,(%esp)
   call   8048660 <decrypt>
   jmp    8048858
 ---> For each case 0..21: call **decrypt(d)** then join common exit.

 804884a: e8 …                  call   rand@plt
 804884f: 89 04 24               mov    %eax,(%esp)
 8048852: e8 …                  call   decrypt
 ---> Default: **decrypt(rand())** when d > 21.

 8048858: …                      leave / ret
 ---> Shared exit from test().
```

## `decrypt`

```text
(gdb) disas decrypt
   0x08048660 <+0>:     push   %ebp
   0x08048661 <+1>:     mov    %esp,%ebp
   ---> Prologue.

   0x08048663 <+3>:     push   %edi
   0x08048664 <+4>:     push   %esi
   ---> Save callee-saved registers (used by repnz scasb / repz cmpsb).

   0x08048665 <+5>:     sub    $0x40,%esp
   ---> Allocate 64 bytes for locals: encrypted buffer at -0x1d, strlen result at -0x24, loop index at -0x28.

   0x08048668 <+8>:     mov    %gs:0x14,%eax
   0x0804866e <+14>:    mov    %eax,-0xc(%ebp)
   0x08048671 <+17>:    xor    %eax,%eax
   ---> Load **stack canary** from TLS and store at -0xc(%ebp).

   0x08048673 <+19>:    movl   $0x757c7d51,-0x1d(%ebp)
   0x0804867a <+26>:    movl   $0x67667360,-0x19(%ebp)
   0x08048681 <+33>:    movl   $0x7b66737e,-0x15(%ebp)
   0x08048688 <+40>:    movl   $0x33617c7d,-0x11(%ebp)
   0x0804868f <+47>:    movb   $0x0,-0xd(%ebp)
   ---> Build 16-byte **encrypted buffer** on the stack + NUL terminator.
   ---> Bytes in memory order: 51 7d 7c 75 60 73 66 67 7e 73 66 7b 7d 7c 61 33 00.

   0x08048693 <+51>:    push   %eax
   0x08048694 <+52>:    xor    %eax,%eax
   0x08048696 <+54>:    je     0x804869b <decrypt+59>
   0x08048698 <+56>:    add    $0x4,%esp
   0x0804869b <+59>:    pop    %eax
   ---> Compiler stack-alignment stub (no functional effect).

   0x0804869c <+60>:    lea    -0x1d(%ebp),%eax
   ---> Load address of encrypted buffer into %eax.

   0x0804869f <+63>:    movl   $0xffffffff,-0x2c(%ebp)
   0x080486a6 <+70>:    mov    %eax,%edx
   0x080486a8 <+72>:    mov    $0x0,%eax
   0x080486ad <+77>:    mov    -0x2c(%ebp),%ecx
   0x080486b0 <+80>:    mov    %edx,%edi
   0x080486b2 <+82>:    repnz scas %es:(%edi),%al
   0x080486b4 <+84>:    mov    %ecx,%eax
   0x080486b6 <+86>:    not    %eax
   0x080486b8 <+88>:    sub    $0x1,%eax
   ---> **strlen(buffer)** via repnz scasb: scan for NUL, compute length = 16.

   0x080486bb <+91>:    mov    %eax,-0x24(%ebp)
   ---> Store **len = 16** at -0x24(%ebp).

   0x080486be <+94>:    movl   $0x0,-0x28(%ebp)
   ---> Initialize loop index **i = 0** at -0x28(%ebp).

   0x080486c5 <+101>:   jmp    0x80486e5 <decrypt+133>
   ---> Jump to loop condition check.

   0x080486c7 <+103>:   lea    -0x1d(%ebp),%eax
   0x080486ca <+106>:   add    -0x28(%ebp),%eax
   0x080486cd <+109>:   movzbl (%eax),%eax
   ---> Load **buffer[i]** as unsigned byte.

   0x080486d0 <+112>:   mov    %eax,%edx
   0x080486d2 <+114>:   mov    0x8(%ebp),%eax
   0x080486d5 <+117>:   xor    %edx,%eax
   ---> **XOR buffer[i] with the key** (first argument at 0x8(%ebp)).

   0x080486d7 <+119>:   mov    %eax,%edx
   0x080486d9 <+121>:   lea    -0x1d(%ebp),%eax
   0x080486dc <+124>:   add    -0x28(%ebp),%eax
   0x080486df <+127>:   mov    %dl,(%eax)
   ---> **buffer[i] = buffer[i] ^ key** — write decrypted byte back.

   0x080486e1 <+129>:   addl   $0x1,-0x28(%ebp)
   ---> **i++**.

   0x080486e5 <+133>:   mov    -0x28(%ebp),%eax
   0x080486e8 <+136>:   cmp    -0x24(%ebp),%eax
   0x080486eb <+139>:   jb     0x80486c7 <decrypt+103>
   ---> Loop while **i < len** (unsigned compare).

   0x080486ed <+141>:   lea    -0x1d(%ebp),%eax
   0x080486f0 <+144>:   mov    %eax,%edx
   0x080486f2 <+146>:   mov    $0x80489c3,%eax
   ---> Load address of **"Congratulations!"** string from .rodata.

   0x080486f7 <+151>:   mov    $0x11,%ecx
   ---> Compare length = **17** bytes (16 chars + NUL).

   0x080486fc <+156>:   mov    %edx,%esi
   0x080486fe <+158>:   mov    %eax,%edi
   0x08048700 <+160>:   repz cmpsb %es:(%edi),%ds:(%esi)
   ---> **strncmp(buffer, "Congratulations!", 17)** via repz cmpsb.

   0x08048702 <+162>:   seta   %dl
   0x08048705 <+165>:   setb   %al
   0x08048708 <+168>:   mov    %edx,%ecx
   0x0804870a <+170>:   sub    %al,%cl
   0x0804870c <+172>:   mov    %ecx,%eax
   0x0804870e <+174>:   movsbl %al,%eax
   ---> Compute strcmp-style return value: 0 if equal, positive/negative otherwise.

   0x08048711 <+177>:   test   %eax,%eax
   0x08048713 <+179>:   jne    0x8048723 <decrypt+195>
   ---> If **not equal** → jump to "Nope" path.

   0x08048715 <+181>:   movl   $0x80489d4,(%esp)
   0x0804871c <+188>:   call   0x80484e0 <system@plt>
   ---> **system("/bin/sh")** — decryption matched, spawn shell.

   0x08048721 <+193>:   jmp    0x804872f <decrypt+207>
   ---> Skip "Nope" path.

   0x08048723 <+195>:   movl   $0x80489dc,(%esp)
   0x0804872a <+202>:   call   0x80484d0 <puts@plt>
   ---> **puts("Nope")** — decryption did not match.

   0x0804872f <+207>:   mov    -0xc(%ebp),%esi
   0x08048732 <+210>:   xor    %gs:0x14,%esi
   0x08048739 <+217>:   je     0x8048740 <decrypt+224>
   0x0804873b <+219>:   call   0x80484c0 <__stack_chk_fail@plt>
   ---> **Stack canary check** before return.

   0x08048740 <+224>:   add    $0x40,%esp
   0x08048743 <+227>:   pop    %esi
   0x08048744 <+228>:   pop    %edi
   0x08048745 <+229>:   pop    %ebp
   0x08048746 <+230>:   ret
   ---> Epilogue: restore stack and return.

End of assembler dump.
```

**Exploitation note:** The encrypted buffer XORed with key **18** (0x12) produces `"Congratulations!"`. Key 18 means `input = 0x1337d00d - 18 = 322424827`.
