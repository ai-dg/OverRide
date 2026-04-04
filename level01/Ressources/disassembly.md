# level01 — `verify_user_name`, `verify_user_pass`, `main`

## `verify_user_name`

```text
08048464 <verify_user_name>:
 8048464: 55                    push   %ebp
 ---> Prologue: save old %ebp.

 8048465: 89 e5                 mov    %esp,%ebp
 ---> New frame pointer.

 8048467: 57                    push   %edi
 8048468: 56                    push   %esi
 ---> Save callee-saved regs used by string compare.

 8048469: 83 ec 10              sub    $0x10,%esp
 ---> Local stack for puts arg alignment.

 804846c: c7 04 24 90 86 04 08  movl   $0x8048690,(%esp)
 ---> Address of "verifying username....\n" for puts.

 8048473: e8 08 ff ff ff        call   8048380 <puts@plt>
 ---> Inform user verification started (side channel / UX).

 8048478: ba 40 a0 04 08        mov    $0x804a040,%edx
 ---> %edx = pointer to global `a_user_name` buffer (fgets destination).

 804847d: b8 a8 86 04 08        mov    $0x80486a8,%eax
 ---> %eax = address of expected string in .rodata ("dat_wil", 7 bytes).

 8048482: b9 07 00 00 00        mov    $0x7,%ecx
 ---> Byte count for compare: 7 characters.

 8048487: 89 d6                 mov    %edx,%esi
 ---> %esi = user buffer (DS string for cmpsb).

 8048489: 89 c7                 mov    %eax,%edi
 ---> %edi = reference string (ES for cmpsb).

 804848b: f3 a6                 repz cmpsb %es:(%edi),%ds:(%esi)
 ---> Byte-by-byte compare while equal; stops at first mismatch or end of 7 bytes.

 804848d: 0f 97 c2              seta   %dl
 8048490: 0f 92 c0              setb   %al
 8048493: 89 d1                 mov    %edx,%ecx
 8048495: 28 c1                 sub    %al,%cl
 8048497: 89 c8                 mov    %ecx,%eax
 8048499: 0f be c0              movsbl %al,%eax
 ---> Build a strcmp-like return in %eax from flags after cmpsb (lexicographic ordering).

 804849c: 83 c4 10              add    $0x10,%esp
 804849f: 5e                    pop    %esi
 80484a0: 5f                    pop    %edi
 80484a1: 5d                    pop    %ebp
 80484a2: c3                    ret
 ---> Epilogue; return value 0 means equal for this compiler pattern.
```

## `verify_user_pass`

```text
080484a3 <verify_user_pass>:
 80484a3: 55                    push   %ebp
 80484a4: 89 e5                 mov    %esp,%ebp
 ---> Standard prologue.

 80484a6: 57                    push   %edi
 80484a7: 56                    push   %esi
 ---> Save regs for compare.

 80484a8: 8b 45 08              mov    0x8(%ebp),%eax
 ---> First argument: pointer to password buffer (stack in main).

 80484ab: 89 c2                 mov    %eax,%edx
 ---> Copy user pointer into %edx for cmpsb source (DS side).

 80484ad: b8 b0 86 04 08        mov    $0x80486b0,%eax
 ---> Address of reference "admin" (5 bytes) in .rodata.

 80484b2: b9 05 00 00 00        mov    $0x5,%ecx
 ---> Compare length 5.

 80484b7: 89 d6                 mov    %edx,%esi
 80484b9: 89 c7                 mov    %eax,%edi
 80484bb: f3 a6                 repz cmpsb %es:(%edi),%ds:(%esi)
 ---> Compare first 5 bytes of user input to "admin".

 80484bd: 0f 97 c2              seta   %dl
 80484c0: 0f 92 c0              setb   %al
 80484c3: 89 d1                 mov    %edx,%ecx
 80484c5: 28 c1                 sub    %al,%cl
 80484c7: 89 c8                 mov    %ecx,%eax
 80484c9: 0f be c0              movsbl %al,%eax
 ---> Same strcmp-style return encoding as verify_user_name.

 80484cc: 5e                    pop    %esi
 80484cd: 5f                    pop    %edi
 80484ce: 5d                    pop    %ebp
 80484cf: c3                    ret
 ---> Return to main with comparison result.
```

## `main`

```text
(gdb) disas main
   0x080484d0 <+0>:     push   %ebp
   ---> Prologue.

   0x080484d1 <+1>:     mov    %esp,%ebp
   ---> Frame setup.

   0x080484d3 <+3>:     push   %edi
   0x080484d4 <+4>:     push   %ebx
   ---> Save registers (later used for memset / pointers).

   0x080484d5 <+5>:     and    $0xfffffff0,%esp
   ---> Align stack to 16 bytes.

   0x080484d8 <+8>:     sub    $0x60,%esp
   ---> Allocate frame (buffers + saved pid / return storage at 0x5c(%esp)).

   0x080484db <+11>:    lea    0x1c(%esp),%ebx
   ---> %ebx = address of password buffer (64 bytes area starting esp+0x1c).

   0x080484df <+15>:    mov    $0x0,%eax
   0x080484e4 <+20>:    mov    $0x10,%edx
   ---> Zero in %eax; 0x10 dwords = 64 bytes to clear.

   0x080484e9 <+25>:    mov    %ebx,%edi
   0x080484eb <+27>:    mov    %edx,%ecx
   0x080484ed <+29>:    rep stos %eax,%es:(%edi)
   ---> memset(password_buf, 0, 64).

   0x080484ef <+31>:    movl   $0x0,0x5c(%esp)
   ---> Initialize local status / temp to 0.

   0x080484f7 <+39>:    movl   $0x80486b8,(%esp)
   0x080484fe <+46>:    call   0x8048380 <puts@plt>
   ---> Print "********* ADMIN LOGIN PROMPT *********".

   0x08048503 <+51>:    mov    $0x80486df,%eax
   0x08048508 <+56>:    mov    %eax,(%esp)
   0x0804850b <+59>:    call   0x8048360 <printf@plt>
   ---> printf("Enter Username: ") (no newline).

   0x08048510 <+64>:    mov    0x804a020,%eax
   ---> Load stdin FILE* from GOT-linked symbol.

   0x08048515 <+69>:    mov    %eax,0x8(%esp)
   ---> Third arg to fgets: stream = stdin.

   0x08048519 <+73>:    movl   $0x100,0x4(%esp)
   ---> Second arg: size 256 (0x100) — reads into global `a_user_name`.

   0x08048521 <+81>:    movl   $0x804a040,(%esp)
   ---> First arg: buffer address (global).

   0x08048528 <+88>:    call   0x8048370 <fgets@plt>
   ---> Read username (bounded; newline may be present).

   0x0804852d <+93>:    call   0x8048464 <verify_user_name>
   ---> Compare global buffer to expected username prefix.

   0x08048532 <+98>:    mov    %eax,0x5c(%esp)
   ---> Store return code.

   0x08048536 <+102>:   cmpl   $0x0,0x5c(%esp)
   0x0804853b <+107>:   je     0x8048550 <main+128>
   ---> If strcmp-style result == 0 (match), continue to password prompt.

   0x0804853d <+109>:   movl   $0x80486f0,(%esp)
   0x08048544 <+116>:   call   0x8048380 <puts@plt>
   ---> Mismatch: print "nope, incorrect username...".

   0x08048549 <+121>:   mov    $0x1,%eax
   0x0804854e <+126>:   jmp    0x80485af <main+223>
   ---> exit main with failure (1).

   0x08048550 <+128>:   movl   $0x804870d,(%esp)
   0x08048557 <+135>:   call   0x8048380 <puts@plt>
   ---> Print "Enter Password: ".

   0x0804855c <+140>:   mov    0x804a020,%eax
   0x08048561 <+145>:   mov    %eax,0x8(%esp)
   ---> stdin for fgets.

   0x08048565 <+149>:   movl   $0x64,0x4(%esp)
   ---> Read at most 100 (0x64) bytes into local password buffer.

   0x0804856d <+157>:   lea    0x1c(%esp),%eax
   0x08048571 <+161>:   mov    %eax,(%esp)
   ---> Pointer to local buffer on stack.

   0x08048574 <+164>:   call   0x8048370 <fgets@plt>
   ---> Read password line.

   0x08048579 <+169>:   lea    0x1c(%esp),%eax
   0x0804857d <+173>:   mov    %eax,(%esp)
   ---> Pass buffer pointer to verify_user_pass.

   0x08048580 <+176>:   call   0x80484a3 <verify_user_pass>
   ---> Compare to "admin" (5 bytes).

   0x08048585 <+181>:   mov    %eax,0x5c(%esp)
   ---> Save return value again.

   0x08048589 <+185>:   cmpl   $0x0,0x5c(%esp)
   0x0804858e <+190>:   je     0x8048597 <main+199>
   ---> First branch on zero (compiler artifact / merged compare).

   0x08048590 <+192>:   cmpl   $0x0,0x5c(%esp)
   0x08048595 <+197>:   je     0x80485aa <main+218>
   ---> Second compare — together encode success vs failure paths for this build.

   0x08048597 <+199>:   movl   $0x804871e,(%esp)
   0x0804859e <+206>:   call   0x8048380 <puts@plt>
   ---> Failure path: "nope, incorrect password...".

   0x080485a3 <+211>:   mov    $0x1,%eax
   0x080485a8 <+216>:   jmp    0x80485af <main+223>
   ---> Return 1.

   0x080485aa <+218>:   mov    $0x0,%eax
   ---> Success: return 0 (both username and password matched).

   0x080485af <+223>:   lea    -0x8(%ebp),%esp
   ---> Restore %esp before popping saved registers.

   0x080485b2 <+226>:   pop    %ebx
   0x080485b3 <+227>:   pop    %edi
   0x080485b4 <+228>:   pop    %ebp
   0x080485b5 <+229>:   ret
   ---> Return to libc with status in %eax.

End of assembler dump.
```

**Exploitation note:** Username and password are length-bounded compares against static strings; the interesting weakness for OverRide is often **overflow elsewhere** or **logic** — confirm in your walkthrough if a different primitive is used.
