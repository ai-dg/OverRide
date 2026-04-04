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

**Exploitation note:** Control **d = 0x1337d00d − input** so that **d ∈ [0,21]** hits a fixed `decrypt` case, or force the **rand** branch. Actual password comes from `decrypt()` logic (not shown here).
