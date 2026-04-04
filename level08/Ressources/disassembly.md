# level08 — `main` and `log_wrapper` (x86-64)

## `main`

```text
(gdb) disas main
   0x00000000004009f0 <+0>:     push   %rbp
   0x00000000004009f1 <+1>:     mov    %rsp,%rbp
   ---> Standard prologue.

   0x00000000004009f4 <+4>:     sub    $0xb0,%rsp
   ---> Stack frame: argc at -0x94, argv at -0xa0, FILE* at -0x88 and -0x80, fd at -0x78, path buffer at -0x70, temp byte at -0x71, canary at -0x8.

   0x00000000004009fb <+11>:    mov    %edi,-0x94(%rbp)
   ---> Save **argc** (System V AMD64: first arg in **rdi**).

   0x0000000000400a01 <+17>:    mov    %rsi,-0xa0(%rbp)
   ---> Save **argv**.

   0x0000000000400a08 <+24>:    mov    %fs:0x28,%rax
   0x0000000000400a11 <+33>:    mov    %rax,-0x8(%rbp)
   0x0000000000400a15 <+37>:    xor    %eax,%eax
   ---> Stack canary.

   0x0000000000400a17 <+39>:    movb   $0xff,-0x71(%rbp)
   ---> Initialize per-byte read buffer to **0xFF** (sentinel before **fgetc** loop).

   0x0000000000400a1b <+43>:    movl   $0xffffffff,-0x78(%rbp)
   ---> **fd = -1** until **open** succeeds.

   0x0000000000400a22 <+50>:    cmpl   $0x2,-0x94(%rbp)
   0x0000000000400a29 <+57>:    je     0x400a4a <main+90>
   ---> Require **argc == 2** (program name + one argument).

   0x0000000000400a2b <+59>:    mov    -0xa0(%rbp),%rax
   0x0000000000400a32 <+66>:    mov    (%rax),%rdx
   0x0000000000400a35 <+69>:    mov    $0x400d57,%eax
   0x0000000000400a3a <+74>:    mov    %rdx,%rsi
   0x0000000000400a3d <+77>:    mov    %rax,%rdi
   0x0000000000400a40 <+80>:    mov    $0x0,%eax
   0x0000000000400a45 <+85>:    callq  0x400730 <printf@plt>
   ---> Usage: **printf** with argv[0] (wrong argc path).

   0x0000000000400a4a <+90>:    mov    $0x400d6b,%edx
   0x0000000000400a4f <+95>:    mov    $0x400d6d,%eax
   0x0000000000400a54 <+100>:   mov    %rdx,%rsi
   0x0000000000400a57 <+103>:   mov    %rax,%rdi
   0x0000000000400a5a <+106>:   callq  0x4007c0 <fopen@plt>
   ---> **fopen("backups/backup.log", "a+")** (mode strings at fixed rodata addresses).

   0x0000000000400a5f <+111>:   mov    %rax,-0x88(%rbp)
   ---> **log FILE\*** stored.

   0x0000000000400a66 <+118>:   cmpq   $0x0,-0x88(%rbp)
   0x0000000000400a6e <+126>:   jne    0x400a91 <main+161>
   ---> If fopen failed, print error and **exit(1)**.

   0x0000000000400a70 <+128>:   ... printf … exit
   ---> Error path.

   0x0000000000400a91 <+161>:   mov    -0xa0(%rbp),%rax
   0x0000000000400a98 <+168>:   add    $0x8,%rax
   0x0000000000400a9c <+172>:   mov    (%rax),%rdx
   ---> **rdx = argv[1]** (user-supplied path string).

   0x0000000000400a9f <+175>:   mov    -0x88(%rbp),%rax
   0x0000000000400aa6 <+182>:   mov    $0x400d96,%esi
   0x0000000000400aab <+187>:   mov    %rax,%rdi
   0x0000000000400aae <+190>:   callq  0x4008c4 <log_wrapper>
   ---> **log_wrapper(log_fp, "LOG: argv[1]")** — copies tag then user path into internal buffer and **fprintf** to log (**strcpy** in wrapper = overflow risk).

   0x0000000000400ab3 <+195>:   mov    $0x400da9,%edx
   0x0000000000400ab8 <+200>:   mov    -0xa0(%rbp),%rax
   0x0000000000400abf <+207>:   add    $0x8,%rax
   0x0000000000400ac3 <+211>:   mov    (%rax),%rax
   0x0000000000400ac6 <+214>:   mov    %rdx,%rsi
   0x0000000000400ac9 <+217>:   mov    %rax,%rdi
   0x0000000000400acc <+220>:   callq  0x4007c0 <fopen@plt>
   ---> **fopen(argv[1], "r")** — open file to exfiltrate / read.

   0x0000000000400ad1 <+225>:   mov    %rax,-0x80(%rbp)
   ---> Second **FILE\*** (data file).

   0x0000000000400ad5 <+229>:   cmpq   $0x0,-0x80(%rbp)
   0x0000000000400ada <+234>:   jne    0x400b09 <main+281>
   ---> If open failed, printf and **exit(1)**.

   0x0000000000400b09 <+281>:   mov    $0x400dab,%edx
   0x0000000000400b0e <+286>:   lea    -0x70(%rbp),%rax
   0x0000000000400b12 <+290>:   mov    (%rdx),%rcx
   0x0000000000400b15 <+293>:   mov    %rcx,(%rax)
   0x0000000000400b18 <+296>:   movzwl 0x8(%rdx),%ecx
   0x0000000000400b1c <+300>:   mov    %cx,0x8(%rax)
   0x0000000000400b20 <+304>:   movzbl 0xa(%rdx),%edx
   0x0000000000400b24 <+308>:   mov    %dl,0xa(%rax)
   ---> Copy **11 bytes** from global rodata (**"./backups/"** prefix) into stack buffer **path[0..10]**.

   0x0000000000400b27 <+311>:   lea    -0x70(%rbp),%rax
   ... repnz scasb … strlen of path prefix
   0x0000000000400b50 <+352>:   lea    -0x1(%rax),%rdx
   ---> **len = strlen(path_prefix)**.

   0x0000000000400b54 <+356>:   mov    $0x63,%eax
   0x0000000000400b59 <+361>:   mov    %rax,%rcx
   0x0000000000400b5c <+364>:   sub    %rdx,%rcx
   0x0000000000400b5f <+367>:   mov    %rcx,%rdx
   ---> **0x63 - len** → remaining space (**99 - strlen**) for **strncat** third argument.

   0x0000000000400b62 <+370>:   mov    -0xa0(%rbp),%rax
   0x0000000000400b69 <+377>:   add    $0x8,%rax
   0x0000000000400b6d <+381>:   mov    (%rax),%rax
   0x0000000000400b70 <+384>:   mov    %rax,%rcx
   0x0000000000400b73 <+387>:   lea    -0x70(%rbp),%rax
   0x0000000000400b77 <+391>:   mov    %rcx,%rsi
   0x0000000000400b7a <+394>:   mov    %rax,%rdi
   0x0000000000400b7d <+397>:   callq  0x400750 <strncat@plt>
   ---> **strncat(path, argv[1], 99 - strlen(prefix))** — build **./backups/<argv[1]>**.

   0x0000000000400b82 <+402>:   lea    -0x70(%rbp),%rax
   0x0000000000400b86 <+406>:   mov    $0x1b0,%edx
   0x0000000000400b8b <+411>:   mov    $0xc1,%esi
   0x0000000000400b90 <+416>:   mov    %rax,%rdi
   0x0000000000400b93 <+419>:   mov    $0x0,%eax
   0x0000000000400b98 <+424>:   callq  0x4007b0 <open@plt>
   ---> **open(path, flags, mode)** — create/write backup file (literals **0xc1** / **0x1b0**).

   0x0000000000400b9d <+429>:   mov    %eax,-0x78(%rbp)
   ---> Save **fd**.

   0x0000000000400ba0 <+432>:   cmpl   $0x0,-0x78(%rbp)
   0x0000000000400ba4 <+436>:   jns    0x400bed <main+509>
   ---> If **fd < 0**, error and exit.

   0x0000000000400bd5 <+485>:   lea    -0x71(%rbp),%rcx
   0x0000000000400bd9 <+489>:   mov    -0x78(%rbp),%eax
   0x0000000000400bdc <+492>:   mov    $0x1,%edx
   0x0000000000400be1 <+497>:   mov    %rcx,%rsi
   0x0000000000400be4 <+500>:   mov    %eax,%edi
   0x0000000000400be6 <+502>:   callq  0x400700 <write@plt>
   ---> **write(fd, &byte, 1)** — copy loop body: write one byte to backup.

   0x0000000000400beb <+507>:   jmp    0x400bee <main+510>
   0x0000000000400bed <+509>:   nop
   0x0000000000400bee <+510>:   mov    -0x80(%rbp),%rax
   0x0000000000400bf2 <+514>:   mov    %rax,%rdi
   0x0000000000400bf5 <+517>:   callq  0x400760 <fgetc@plt>
   0x0000000000400bfa <+522>:   mov    %al,-0x71(%rbp)
   0x0000000000400bfd <+525>:   movzbl -0x71(%rbp),%eax
   0x0000000000400c01 <+529>:   cmp    $0xff,%al
   0x0000000000400c03 <+531>:   jne    0x400bd5 <main+485>
   ---> Read from source **FILE\*** with **fgetc** until **EOF (0xFF as byte comparison)** — typical **while ((c=fgetc)!=EOF)** pattern with char stored in **-0x71**.

   0x0000000000400c05 <+533>:   mov    -0xa0(%rbp),%rax
   ... log_wrapper again, fclose, close
   ---> After copy: log completion, **fclose** data file, **close** backup fd.

   0x0000000000400c3d <+589>:   mov    $0x0,%eax
   0x0000000000400c42 <+594>:   mov    -0x8(%rbp),%rdi
   0x0000000000400c46 <+598>:   xor    %fs:0x28,%rdi
   0x0000000000400c4f <+607>:   je     0x400c56 <main+614>
   0x0000000000400c51 <+609>:   callq  0x400720 <__stack_chk_fail@plt>
   0x0000000000400c56 <+614>:   leaveq
   0x0000000000400c57 <+615>:   retq
   ---> Return 0; canary check.

End of assembler dump.
```

## `log_wrapper`

```text
(gdb) disas log_wrapper
   0x00000000004008c4 <+0>:     push   %rbp
   0x00000000004008c5 <+1>:     mov    %rsp,%rbp
   0x00000000004008c8 <+4>:     sub    $0x130,%rsp
   ---> Large local buffer **-0x110(%rbp)** (~256 bytes) for log line.

   0x00000000004008cf <+11>:    mov    %rdi,-0x118(%rbp)
   0x00000000004008d6 <+18>:    mov    %rsi,-0x120(%rbp)
   0x00000000004008dd <+25>:    mov    %rdx,-0x128(%rbp)
   ---> Args: **FILE\***, **msg** string, optional third (unused in first strcpy path).

   0x00000000004008e4 <+32>:    mov    %fs:0x28,%rax
   ... canary at -0x8(%rbp)

   0x00000000004008f3 <+47>:    mov    -0x120(%rbp),%rdx
   0x00000000004008fa <+54>:    lea    -0x110(%rbp),%rax
   0x0000000000400901 <+61>:    mov    %rdx,%rsi
   0x0000000000400904 <+64>:    mov    %rax,%rdi
   0x0000000000400907 <+67>:    callq  0x4006f0 <strcpy@plt>
   ---> **strcpy(buf, msg)** — **unbounded copy** into ~256-byte **buf**; core vulnerability if **msg** is long.

   0x000000000040090c <+72>:    mov    -0x128(%rbp),%rsi
   ... two strlen passes …
   0x0000000000400996 <+210>:   callq  0x400740 <snprintf@plt>
   ---> **snprintf** appends user path segment with computed max length (**0xfe − len** style).

   0x000000000040099b <+215>:   lea    -0x110(%rbp),%rax
   0x00000000004009a2 <+222>:   mov    $0x400d4c,%esi
   0x00000000004009a7 <+227>:   mov    %rax,%rdi
   0x00000000004009aa <+230>:   callq  0x400780 <strcspn@plt>
   0x00000000004009af <+235>:   movb   $0x0,-0x110(%rbp,%rax,1)
   ---> **strcspn(buf, "\n")** then NUL at first newline — sanitize line.

   0x00000000004009b7 <+243>:   mov    $0x400d4e,%ecx
   0x00000000004009bc <+248>:   lea    -0x110(%rbp),%rdx
   0x00000000004009c3 <+255>:   mov    -0x118(%rbp),%rax
   0x00000000004009ca <+262>:   mov    %rcx,%rsi
   0x00000000004009cd <+265>:   mov    %rax,%rdi
   0x00000000004009d0 <+268>:   mov    $0x0,%eax
   0x00000000004009d5 <+273>:   callq  0x4007a0 <fprintf@plt>
   ---> **fprintf(FILE, "format", buf)** — write log line.

   0x00000000004009da <+278>:   ... canary check … leave … ret

End of assembler dump.
```

**Exploitation note:** **strcpy** into a fixed stack buffer enables **stack buffer overflow**; second phase uses **strncat** / **open** with a path under **./backups/**. Exact offsets belong in GDB notes.
