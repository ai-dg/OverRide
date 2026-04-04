# level04 — `main` (fork / ptrace / `gets`)

```text
(gdb) disas main
   0x080486c8 <+0>:     push   %ebp
   ---> Prologue.

   0x080486c9 <+1>:     mov    %esp,%ebp
   ---> Frame setup.

   0x080486cb <+3>:     push   %edi
   0x080486cc <+4>:     push   %ebx
   ---> Save callee-saved registers.

   0x080486cd <+5>:     and    $0xfffffff0,%esp
   ---> Align stack.

   0x080486d0 <+8>:     sub    $0xb0,%esp
   ---> Large frame: 128-byte shellcode buffer at esp+0x20, wait status at esp+0x1c, pid at esp+0xac, etc.

   0x080486d6 <+14>:    call   0x8048550 <fork@plt>
   ---> Create child (tracer) and parent (tracee) or inverse depending on return.

   0x080486db <+19>:    mov    %eax,0xac(%esp)
   ---> Store PID result of fork.

   0x080486e2 <+26>:    lea    0x20(%esp),%ebx
   ---> Pointer to 128-byte buffer (later passed to gets).

   0x080486e6 <+30>:    mov    $0x0,%eax
   0x080486eb <+35>:    mov    $0x20,%edx
   0x080486f0 <+40>:    mov    %ebx,%edi
   0x080486f2 <+42>:    mov    %edx,%ecx
   0x080486f4 <+44>:    rep stos %eax,%es:(%edi)
   ---> memset(buf, 0, 128) — 0x20 dwords.

   0x080486f6 <+46>:    movl   $0x0,0xa8(%esp)
   ---> Clear ptrace peek result slot.

   0x08048701 <+57>:    movl   $0x0,0x1c(%esp)
   ---> Clear wait status word.

   0x08048709 <+65>:    cmpl   $0x0,0xac(%esp)
   0x08048711 <+73>:    jne    0x8048769 <main+161>
   ---> If fork returned **non-zero**, we are **parent** → jump to wait/ptrace loop.

   0x08048713 <+75>:    movl   $0x1,0x4(%esp)
   0x0804871b <+83>:    movl   $0x1,(%esp)
   0x08048722 <+90>:    call   0x8048540 <prctl@plt>
   ---> Child: **prctl(1, 1)** (e.g. PR_SET_PDEATHSIG) — environment hardening.

   0x08048727 <+95>:    movl   $0x0,0xc(%esp)
   0x0804872f <+103>:   movl   $0x0,0x8(%esp)
   0x08048737 <+111>:   movl   $0x0,0x4(%esp)
   0x0804873f <+119>:   movl   $0x0,(%esp)
   0x08048746 <+126>:   call   0x8048570 <ptrace@plt>
   ---> **ptrace(PTRACE_TRACEME, 0, 0, 0)** — child asks to be traced.

   0x0804874b <+131>:   movl   $0x8048903,(%esp)
   0x08048752 <+138>:   call   0x8048500 <puts@plt>
   ---> Prompt: "Give me some shellcode, k".

   0x08048757 <+143>:   lea    0x20(%esp),%eax
   0x0804875b <+147>:   mov    %eax,(%esp)
   0x0804875e <+150>:   call   0x80484b0 <gets@plt>
   ---> **gets(buf)** — unbounded read; **stack overflow** primitive.

   0x08048763 <+155>:   jmp    0x804881a <main+338>
   ---> Child skips parent loop; jumps to shared return (exit main).

   0x08048768 <+160>:   nop
   ---> Padding / alignment.

   0x08048769 <+161>:   lea    0x1c(%esp),%eax
   0x0804876d <+165>:   mov    %eax,(%esp)
   0x08048770 <+168>:   call   0x80484f0 <wait@plt>
   ---> Parent: **wait(&status)** — reaps child stops.

   0x08048775 <+173>:   mov    0x1c(%esp),%eax
   ... through 0x080487aa
   ---> Decode **wait status**: detect normal exit vs stop-for-signal (child exit path).

   0x080487ac <+228>:   movl   $0x804891d,(%esp)
   0x080487b3 <+235>:   call   0x8048500 <puts@plt>
   0x080487b8 <+240>:   jmp    0x804881a <main+338>
   ---> "child is exiting..." branch if process ended.

   0x080487ba <+242>:   movl   $0x0,0xc(%esp)
   0x080487c2 <+250>:   movl   $0x2c,0x8(%esp)
   0x080487ca <+258>:   mov    0xac(%esp),%eax
   0x080487d1 <+265>:   mov    %eax,0x4(%esp)
   0x080487d5 <+269>:   movl   $0x3,(%esp)
   0x080487dc <+276>:   call   0x8048570 <ptrace@plt>
   ---> **ptrace(PTRACE_PEEKUSER, pid, 0x2c, 0)** — read **orig_eax** (syscall number) on i386.

   0x080487e1 <+281>:   mov    %eax,0xa8(%esp)
   0x080487e8 <+288>:   cmpl   $0xb,0xa8(%esp)
   0x080487f0 <+296>:   jne    0x8048768 <main+160>
   ---> Loop until syscall number **0xb** (**execve**). Otherwise continue waiting.

   0x080487f6 <+302>:   movl   $0x8048931,(%esp)
   0x080487fd <+309>:   call   0x8048500 <puts@plt>
   ---> Detected execve: print "no exec() for you".

   0x08048802 <+314>:   movl   $0x9,0x4(%esp)
   0x0804880a <+322>:   mov    0xac(%esp),%eax
   0x08048811 <+329>:   mov    %eax,(%esp)
   0x08048814 <+332>:   call   0x8048520 <kill@plt>
   ---> **kill(pid, SIGKILL)** — stop child before exec.

   0x08048819 <+337>:   nop

   0x0804881a <+338>:   mov    $0x0,%eax
   0x0804881f <+343>:   lea    -0x8(%ebp),%esp
   0x08048822 <+346>:   pop    %ebx
   0x08048823 <+347>:   pop    %edi
   0x08048824 <+348>:   pop    %ebp
   0x08048825 <+349>:   ret
   ---> Return 0 from main.

End of assembler dump.
```

**Exploitation note:** **gets** enables overflow; parent blocks **execve** (syscall 11) via ptrace — typical goal is **return-oriented** or **non-exec** shellcode, or **debug bypass** tricks per your walkthrough.
