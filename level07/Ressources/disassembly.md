# level07 — `main`, `store_number`, `read_number`

## `main`

```text
(gdb) disas main
   0x08048723 <+0>:     push   %ebp
   ---> Save caller’s frame pointer.

   0x08048724 <+1>:     mov    %esp,%ebp
   ---> New frame.

   0x08048726 <+3>:     push   %edi
   0x08048727 <+4>:     push   %esi
   0x08048728 <+5>:     push   %ebx
   ---> Callee-saved registers (long main uses them in loops).

   0x08048729 <+6>:     and    $0xfffffff0,%esp
   ---> Stack alignment.

   0x0804872c <+9>:     sub    $0x1d0,%esp
   ---> Large frame: number array at esp+0x24, argv/env pointers, command line, canary, flags.

   0x08048732 <+15>:    mov    0xc(%ebp),%eax
   0x08048735 <+18>:    mov    %eax,0x1c(%esp)
   ---> Copy **argv** to stack slot.

   0x08048739 <+22>:    mov    0x10(%ebp),%eax
   0x0804873c <+25>:    mov    %eax,0x18(%esp)
   ---> Copy **envp** to stack slot.

   0x08048740 <+29>:    mov    %gs:0x14,%eax
   0x08048746 <+35>:    mov    %eax,0x1cc(%esp)
   0x0804874d <+42>:    xor    %eax,%eax
   ---> Stack canary from TLS into frame.

   0x0804874f <+44>:    movl   $0x0,0x1b4(%esp)
   ... through 0x08048786
   ---> Zero five dwords: parsed command fields / state (store success flag and related).

   0x08048791 <+110>:   lea    0x24(%esp),%ebx
   ---> **ebx** = base of **int array[100]** (400 bytes).

   0x08048795 <+114>:   mov    $0x0,%eax
   0x0804879a <+119>:   mov    $0x64,%edx
   0x0804879f <+124>:   mov    %ebx,%edi
   0x080487a1 <+126>:   mov    %edx,%ecx
   0x080487a3 <+128>:   rep stos %eax,%es:(%edi)
   ---> **memset(array, 0, 400)** — 100 × 4 bytes.

   0x080487a5 <+130>:   jmp    0x80487ea <main+199>
   ---> Jump to **argv wipe loop** test.

   0x080487a7 <+132>:   mov    0x1c(%esp),%eax
   0x080487ab <+136>:   mov    (%eax),%eax
   ---> Load current **argv[i]** pointer.

   0x080487ad <+138>:   movl   $0xffffffff,0x14(%esp)
   ... repnz scasb … not … lea -1
   ---> **strlen(argv[i])** via scasb.

   0x080487cb <+168>:   mov    0x1c(%esp),%eax
   0x080487cf <+172>:   mov    (%eax),%eax
   0x080487d1 <+174>:   mov    %edx,0x8(%esp)
   0x080487d5 <+178>:   movl   $0x0,0x4(%esp)
   0x080487dd <+186>:   mov    %eax,(%esp)
   0x080487e0 <+189>:   call   0x80484f0 <memset@plt>
   ---> **memset(argv[i], 0, len)** — clear each argument string in memory.

   0x080487e5 <+194>:   addl   $0x4,0x1c(%esp)
   ---> **argv++** (pointer to next char*).

   0x080487ea <+199>:   mov    0x1c(%esp),%eax
   0x080487ee <+203>:   mov    (%eax),%eax
   0x080487f0 <+205>:   test   %eax,%eax
   0x080487f2 <+207>:   jne    0x80487a7 <main+132>
   ---> Loop until **argv[i] == NULL**.

   0x080487f4 <+209>:   jmp    0x8048839 <main+278>
   ---> Finished argv; jump to **envp wipe** entry.

   0x080487f6 <+211>:   mov    0x18(%esp),%eax
   ... (same memset pattern on env strings)
   ---> **memset(env_var, 0, strlen)** for each **environ** entry.

   0x08048834 <+273>:   addl   $0x4,0x18(%esp)
   ---> Advance **envp** pointer.

   0x08048839 <+278>:   mov    0x18(%esp),%eax
   0x0804883d <+282>:   mov    (%eax),%eax
   0x0804883f <+284>:   test   %eax,%eax
   0x08048841 <+286>:   jne    0x80487f6 <main+211>
   ---> Loop until **envp[i] == NULL**.

   0x08048843 <+288>:   movl   $0x8048b38,(%esp)
   0x0804884a <+295>:   call   0x80484c0 <puts@plt>
   ---> Banner: “DATA REL RO …” (welcome).

   0x0804884f <+300>:   mov    $0x8048d4b,%eax
   0x08048854 <+305>:   mov    %eax,(%esp)
   0x08048857 <+308>:   call   0x8048470 <printf@plt>
   ---> Print command menu / prompt.

   0x0804885c <+313>:   movl   $0x1,0x1b4(%esp)
   ---> Set “continue loop” flag (non-zero).

   0x08048867 <+324>:   mov    0x804a040,%eax
   0x0804886c <+329>:   mov    %eax,0x8(%esp)
   0x08048870 <+333>:   movl   $0x14,0x4(%esp)
   0x08048878 <+341>:   lea    0x1b8(%esp),%eax
   0x0804887f <+348>:   mov    %eax,(%esp)
   0x08048882 <+351>:   call   0x80484a0 <fgets@plt>
   ---> **fgets(cmdline, 0x14, stdin)** — short command buffer.

   0x08048887 <+356>:   lea    0x1b8(%esp),%eax
   ... repnz scasb … not … sub 1 twice
   ---> **Strip trailing newline**: find length, write NUL at last non-newline.

   0x080488af <+396>:   movb   $0x0,0x1b8(%esp,%eax,1)
   ---> Terminate string after strip.

   0x080488b7 <+404>:   lea    0x1b8(%esp),%eax
   0x080488be <+411>:   mov    %eax,%edx
   0x080488c0 <+413>:   mov    $0x8048d5b,%eax
   0x080488c5 <+418>:   mov    $0x5,%ecx
   0x080488ca <+423>:   mov    %edx,%esi
   0x080488cc <+425>:   mov    %eax,%edi
   0x080488ce <+427>:   repz cmpsb %es:(%edi),%ds:(%esi)
   ... seta/setb/sub
   ---> **strncmp**-style compare to **"store"** (5 bytes).

   0x080488e1 <+446>:   jne    0x80488f8 <main+469>
   0x080488e3 <+448>:   lea    0x24(%esp),%eax
   0x080488e7 <+452>:   mov    %eax,(%esp)
   0x080488ea <+455>:   call   0x8048630 <store_number>
   0x080488ef <+460>:   mov    %eax,0x1b4(%esp)
   0x080488f6 <+467>:   jmp    0x8048965 <main+578>
   ---> If command is **store**, call **store_number(&array)**; save return in flag slot.

   0x080488f8 <+469>:   lea    0x1b8(%esp),%eax
   ... repz cmpsb vs **"read"** (4 bytes)
   0x08048922 <+511>:   jne    0x8048939 <main+534>
   0x08048924 <+513>:   lea    0x24(%esp),%eax
   0x08048928 <+517>:   mov    %eax,(%esp)
   0x0804892b <+520>:   call   0x80486d7 <read_number>
   ---> Else if **read**, call **read_number(&array)**.

   0x08048930 <+525>:   mov    %eax,0x1b4(%esp)
   0x08048937 <+532>:   jmp    0x8048965 <main+578>

   0x08048939 <+534>:   lea    0x1b8(%esp),%eax
   ... compare to **"exit"**
   0x08048963 <+576>:   je     0x80489cf <main+684>
   ---> If **exit**, leave loop (fall through to epilogue).

   0x08048965 <+578>:   cmpl   $0x0,0x1b4(%esp)
   0x0804896d <+586>:   je     0x8048989 <main+614>
   ---> If last subcall returned **0**, print failure message branch.

   0x0804896f <+588>:   mov    $0x8048d6b,%eax
   ... printf with cmdline
   ---> **Error** printf (operation failed).

   0x08048989 <+614>:   mov    $0x8048d88,%eax
   ... printf
   ---> **Success** printf path.

   0x080489a1 <+638>:   lea    0x1b8(%esp),%eax
   0x080489a8 <+645>:   movl   $0x0,(%eax)
   ... zero 20 bytes at cmdline
   ---> Clear command buffer for next iteration.

   0x080489ca <+679>:   jmp    0x804884f <main+300>
   ---> Loop back to menu **printf** / **fgets**.

   0x080489cf <+684>:   nop
   0x080489d0 <+685>:   mov    $0x0,%eax
   ---> **exit** command: return 0 from main.

   0x080489d5 <+690>:   mov    0x1cc(%esp),%esi
   0x080489dc <+697>:   xor    %gs:0x14,%esi
   0x080489e3 <+704>:   je     0x80489ea <main+711>
   0x080489e5 <+706>:   call   0x80484b0 <__stack_chk_fail@plt>
   ---> Canary check.

   0x080489ea <+711>:   lea    -0xc(%ebp),%esp
   0x080489ed <+714>:   pop    %ebx
   0x080489ee <+715>:   pop    %esi
   0x080489ef <+716>:   pop    %edi
   0x080489f0 <+717>:   pop    %ebp
   0x080489f1 <+718>:   ret
   ---> Epilogue.

End of assembler dump.
```

## `read_number`

```text
(gdb) disas read_number
   0x080486d7 <+0>:     push   %ebp
   0x080486d8 <+1>:     mov    %esp,%ebp
   0x080486da <+3>:     sub    $0x28,%esp
   ---> Frame; local **index** at -0xc.

   0x080486dd <+6>:     movl   $0x0,-0xc(%ebp)
   ---> index = 0 (redundant before get_unum overwrites).

   0x080486e4 <+13>:    mov    $0x8048add,%eax
   0x080486e9 <+18>:    mov    %eax,(%esp)
   0x080486ec <+21>:    call   0x8048470 <printf@plt>
   ---> Prompt: “Index:” (or similar).

   0x080486f1 <+26>:    call   0x80485e7 <get_unum>
   ---> Read **unsigned** decimal (no negatives/spaces) into **eax**.

   0x080486f6 <+31>:    mov    %eax,-0xc(%ebp)
   ---> Store **index**.

   0x080486f9 <+34>:    mov    -0xc(%ebp),%eax
   0x080486fc <+37>:    shl    $0x2,%eax
   0x080486ff <+40>:    add    0x8(%ebp),%eax
   0x08048702 <+43>:    mov    (%eax),%edx
   ---> **edx = array[index]** (scaled index).

   0x08048704 <+45>:    mov    $0x8048b1b,%eax
   0x08048709 <+50>:    mov    %edx,0x8(%esp)
   0x0804870d <+54>:    mov    -0xc(%ebp),%edx
   0x08048710 <+57>:    mov    %edx,0x4(%esp)
   0x08048714 <+61>:    mov    %eax,(%esp)
   0x08048717 <+64>:    call   0x8048470 <printf@plt>
   ---> **printf(fmt, index, value)** — print stored number.

   0x0804871c <+69>:    mov    $0x0,%eax
   ---> Return **0** (success).

   0x08048721 <+74>:    leave
   0x08048722 <+75>:    ret

End of assembler dump.
```

## `store_number`

```text
(gdb) disas store_number
   0x08048630 <+0>:     push   %ebp
   0x08048631 <+1>:     mov    %esp,%ebp
   0x08048633 <+3>:     sub    $0x28,%esp
   ---> Locals: **number** at -0x10, **index** at -0xc.

   0x08048636 <+6>:     movl   $0x0,-0x10(%ebp)
   0x0804863d <+13>:    movl   $0x0,-0xc(%ebp)
   ---> Initialize (overwritten immediately).

   0x08048644 <+20>:    mov    $0x8048ad3,%eax
   0x08048649 <+25>:    mov    %eax,(%esp)
   0x0804864c <+28>:    call   0x8048470 <printf@plt>
   ---> Prompt: “Number:”.

   0x08048651 <+33>:    call   0x80485e7 <get_unum>
   0x08048656 <+38>:    mov    %eax,-0x10(%ebp)
   ---> Read **number**.

   0x08048659 <+41>:    mov    $0x8048add,%eax
   0x0804865e <+46>:    mov    %eax,(%esp)
   0x08048661 <+49>:    call   0x8048470 <printf@plt>
   ---> Prompt: “Index:”.

   0x08048666 <+54>:    call   0x80485e7 <get_unum>
   0x0804866b <+59>:    mov    %eax,-0xc(%ebp)
   ---> Read **index**.

   0x0804866e <+62>:    mov    -0xc(%ebp),%ecx
   0x08048671 <+65>:    mov    $0xaaaaaaab,%edx
   0x08048676 <+70>:    mov    %ecx,%eax
   0x08048678 <+72>:    mul    %edx
   0x0804867a <+74>:    shr    %edx
   0x0804867c <+76>:    mov    %edx,%eax
   0x0804867e <+78>:    add    %eax,%eax
   0x08048680 <+80>:    add    %edx,%eax
   0x08048682 <+82>:    mov    %ecx,%edx
   0x08048684 <+84>:    sub    %eax,%edx
   0x08048686 <+86>:    test   %edx,%edx
   0x08048688 <+88>:    je     0x8048697 <store_number+103>
   ---> **index % 3 == 0** check (multiply by magic 0xAAAAAAAB is fast **div by 3** for 32-bit).

   0x0804868a <+90>:    mov    -0x10(%ebp),%eax
   0x0804868d <+93>:    shr    $0x18,%eax
   0x08048690 <+96>:    cmp    $0xb7,%eax
   0x08048695 <+101>:   jne    0x80486c2 <store_number+146>
   ---> If index **not** multiple of 3: require **(number >> 24) == 0xb7** (byte check on high bits — “anti trivial write”).

   0x08048697 <+103>:   movl   $0x8048ae6,(%esp)
   ... puts ×3
   ---> Error messages for invalid store.

   0x080486bb <+139>:   mov    $0x1,%eax
   0x080486c0 <+144>:   jmp    0x80486d5 <store_number+165>
   ---> Return **1** (failure).

   0x080486c2 <+146>:   mov    -0xc(%ebp),%eax
   0x080486c5 <+149>:   shl    $0x2,%eax
   0x080486c8 <+152>:   add    0x8(%ebp),%eax
   0x080486cb <+155>:   mov    -0x10(%ebp),%edx
   0x080486ce <+158>:   mov    %edx,(%eax)
   ---> **array[index] = number** — the actual write.

   0x080486d0 <+160>:   mov    $0x0,%eax
   ---> Return **0** (success).

   0x080486d5 <+165>:   leave
   0x080486d6 <+166>:   ret

End of assembler dump.
```


## `get_unum`

```text
(gdb) disas get_unum
   0x080485e7 <+0>:     push   %ebp
   0x080485e8 <+1>:     mov    %esp,%ebp
   ---> Prologue.

   0x080485ea <+3>:     sub    $0x28,%esp
   ---> Allocate 40 bytes for locals.

   0x080485ed <+6>:     movl   $0x0,-0xc(%ebp)
   ---> Initialize local variable **num = 0** at -0xc(%ebp).

   0x080485f4 <+13>:    mov    0x804a060,%eax
   0x080485f9 <+18>:    mov    %eax,(%esp)
   0x080485fc <+21>:    call   0x8048480 <fflush@plt>
   ---> **fflush(stdout)** — flush output before reading input.

   0x08048601 <+26>:    mov    $0x8048ad0,%eax
   ---> Load format string **"%u"** from .rodata.

   0x08048606 <+31>:    lea    -0xc(%ebp),%edx
   0x08048609 <+34>:    mov    %edx,0x4(%esp)
   0x0804860d <+38>:    mov    %eax,(%esp)
   0x08048610 <+41>:    call   0x8048500 <__isoc99_scanf@plt>
   ---> **scanf("%u", &num)** — read an unsigned integer from stdin.

   0x08048615 <+46>:    call   0x80485c4 <clear_stdin>
   ---> **clear_stdin()** — consume remaining characters in the input buffer.

   0x0804861a <+51>:    mov    -0xc(%ebp),%eax
   ---> Load **num** into return register.

   0x0804861d <+54>:    leave  
   0x0804861e <+55>:    ret    
   ---> Epilogue: return num.

End of assembler dump.
```

**Exploitation note:** The **int array** and weak checks on **index** allow writing outside the intended range (integer overflow on index × 4). **Wiped argv/env** removes easy libc leaks from stack.
