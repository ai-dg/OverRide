# level09 — `main`, `handle_msg`, `set_username`, `set_msg` (x86-64)

## `main`

```text
(gdb) disas main
   0x0000000000000aa8 <+0>:     push   %rbp
   0x0000000000000aa9 <+1>:     mov    %rsp,%rbp
   ---> Prologue.

   0x0000000000000aac <+4>:     lea    0x15d(%rip),%rdi        # 0xc10
   0x0000000000000ab3 <+11>:    callq  0x730 <puts@plt>
   ---> **puts** banner string (RIP-relative LEA).

   0x0000000000000ab8 <+16>:    callq  0x8c0 <handle_msg>
   ---> All program logic in **handle_msg()**.

   0x0000000000000abd <+21>:    mov    $0x0,%eax
   ---> Return **0**.

   0x0000000000000ac2 <+26>:    pop    %rbp
   0x0000000000000ac3 <+27>:    retq
   ---> Epilogue.

End of assembler dump.
```

## `handle_msg`

```text
(gdb) disas handle_msg
   0x00000000000008c0 <+0>:     push   %rbp
   0x00000000000008c1 <+1>:     mov    %rsp,%rbp
   0x00000000000008c4 <+4>:     sub    $0xc0,%rsp
   ---> Frame **0xC0** bytes: large structure at **-0xc0(%rbp)** (message object: username chunk + msg buffer + length field).

   0x00000000000008cb <+11>:    lea    -0xc0(%rbp),%rax
   0x00000000000008d2 <+18>:    add    $0x8c,%rax
   0x00000000000008d8 <+24>:    movq   $0x0,(%rax)
   ... zero 0x28 bytes at rax
   ---> **memset**-style clear of a sub-region starting at **obj+0x8c** (e.g. message body / padding).

   0x00000000000008ff <+63>:    movl   $0x8c,-0xc(%rbp)
   ---> Store **140** in a local — often **max copy length** or structure field.

   0x0000000000000906 <+70>:    lea    -0xc0(%rbp),%rax
   0x000000000000090d <+77>:    mov    %rax,%rdi
   0x0000000000000910 <+80>:    callq  0x9cd <set_username>
   ---> **set_username(&obj)** — fills username into object.

   0x0000000000000915 <+85>:    lea    -0xc0(%rbp),%rax
   0x000000000000091c <+92>:    mov    %rax,%rdi
   0x000000000000091f <+95>:    callq  0x932 <set_msg>
   ---> **set_msg(&obj)** — reads long message and copies into object.

   0x0000000000000924 <+100>:   lea    0x295(%rip),%rdi        # 0xbc0
   0x000000000000092b <+107>:   callq  0x730 <puts@plt>
   ---> Final **puts** (success / goodbye).

   0x0000000000000930 <+112>:   leaveq
   0x0000000000000931 <+113>:   retq

End of assembler dump.
```

## `set_username`

```text
(gdb) disas set_username
   0x00000000000009cd <+0>:     push   %rbp
   0x00000000000009ce <+1>:     mov    %rsp,%rbp
   0x00000000000009d1 <+4>:     sub    $0xa0,%rsp
   ---> Locals: temp buffer **-0x90(%rbp)**, pointer to object **-0x98(%rbp)**.

   0x00000000000009d8 <+11>:    mov    %rdi,-0x98(%rbp)
   ---> Save **struct pointer** argument.

   0x00000000000009df <+18>:    lea    -0x90(%rbp),%rax
   ... rep stosb: 16 × 8 bytes = **0x10 qwords** cleared
   ---> **memset(local, 0, 0x80)** — 128-byte read buffer zeroed.

   0x00000000000009fc <+47>:    lea    0x1e1(%rip),%rdi        # 0xbe4
   0x0000000000000a03 <+54>:    callq  0x730 <puts@plt>
   ---> Prompt line.

   0x0000000000000a08 <+59>:    lea    0x1d0(%rip),%rax        # 0xbdf
   0x0000000000000a0f <+66>:    mov    %rax,%rdi
   0x0000000000000a12 <+69>:    mov    $0x0,%eax
   0x0000000000000a17 <+74>:    callq  0x750 <printf@plt>
   ---> **printf** sub-prompt (e.g. “>> ”).

   0x0000000000000a1c <+79>:    mov    0x201595(%rip),%rax        # 0x201fb8
   0x0000000000000a23 <+86>:    mov    (%rax),%rax
   0x0000000000000a26 <+89>:    mov    %rax,%rdx
   0x0000000000000a29 <+92>:    lea    -0x90(%rbp),%rax
   0x0000000000000a30 <+99>:    mov    $0x80,%esi
   0x0000000000000a35 <+104>:   mov    %rax,%rdi
   0x0000000000000a38 <+107>:   callq  0x770 <fgets@plt>
   ---> **fgets(buf, 0x80, stdin)**.

   0x0000000000000a3d <+112>:   movl   $0x0,-0x4(%rbp)
   ---> **i = 0**.

   0x0000000000000a44 <+119>:   jmp    0xa6a <set_username+157>
   ---> Jump to loop test.

   0x0000000000000a46 <+121>:   mov    -0x4(%rbp),%eax
   0x0000000000000a49 <+124>:   cltq
   0x0000000000000a4b <+126>:   movzbl -0x90(%rbp,%rax,1),%ecx
   0x0000000000000a53 <+134>:   mov    -0x98(%rbp),%rdx
   0x0000000000000a5a <+141>:   mov    -0x4(%rbp),%eax
   0x0000000000000a5d <+144>:   cltq
   0x0000000000000a5f <+146>:   mov    %cl,0x8c(%rdx,%rax,1)
   0x0000000000000a66 <+153>:   addl   $0x1,-0x4(%rbp)
   ---> **obj->username[i] = buf[i]** at offset **0x8c** from object base — copy byte by byte.

   0x0000000000000a6a <+157>:   cmpl   $0x28,-0x4(%rbp)
   0x0000000000000a6e <+161>:   jg     0xa81 <set_username+180>
   0x0000000000000a70 <+163>:   mov    -0x4(%rbp),%eax
   ... load buf[i], test NUL
   0x0000000000000a7f <+178>:   jne    0xa46 <set_username+121>
   ---> Loop until **i > 40 (0x28)** OR **buf[i] == 0** — at most **41** bytes of username into **obj+0x8c** (overlaps next field — **heap layout** / overflow).

   0x0000000000000a81 <+180>:   mov    -0x98(%rbp),%rax
   0x0000000000000a88 <+187>:   lea    0x8c(%rax),%rdx
   0x0000000000000a8f <+194>:   lea    0x165(%rip),%rax        # 0xbfa
   0x0000000000000a96 <+201>:   mov    %rdx,%rsi
   0x0000000000000a99 <+204>:   mov    %rax,%rdi
   0x0000000000000a9c <+207>:   mov    $0x0,%eax
   0x0000000000000aa1 <+212>:   callq  0x750 <printf@plt>
   ---> **printf("… %s …", obj->username)** — confirms username at **+0x8c**.

   0x0000000000000aa6 <+217>:   leaveq
   0x0000000000000aa7 <+218>:   retq

End of assembler dump.
```

## `set_msg`

```text
(gdb) disas set_msg
   0x0000000000000932 <+0>:     push   %rbp
   0x0000000000000933 <+1>:     mov    %rsp,%rbp
   0x0000000000000936 <+4>:     sub    $0x410,%rsp
   ---> Large stack buffer **-0x400(%rbp)** (1024 bytes) for message text; **obj** at **-0x408(%rbp)**.

   0x000000000000093d <+11>:    mov    %rdi,-0x408(%rbp)
   ---> Save object pointer.

   0x0000000000000944 <+18>:    lea    -0x400(%rbp),%rax
   ... rep stos: **0x80** qwords → **0x400** bytes zeroed
   ---> **memset(msgbuf, 0, 1024)**.

   0x0000000000000961 <+47>:    lea    0x265(%rip),%rdi        # 0xbcd
   0x0000000000000968 <+54>:    callq  0x730 <puts@plt>
   0x000000000000096d <+59>:    lea    0x26b(%rip),%rax        # 0xbdf
   ... printf …
   ---> Prompts for message.

   0x0000000000000981 <+79>:    mov    0x201630(%rip),%rax        # 0x201fb8
   0x0000000000000988 <+86>:    mov    (%rax),%rax
   0x000000000000098b <+89>:    mov    %rax,%rdx
   0x000000000000098e <+92>:    lea    -0x400(%rbp),%rax
   0x0000000000000995 <+99>:    mov    $0x400,%esi
   0x000000000000099a <+104>:   mov    %rax,%rdi
   0x000000000000099d <+107>:   callq  0x770 <fgets@plt>
   ---> **fgets(msgbuf, 0x400, stdin)** — up to **1023** chars + NUL.

   0x00000000000009a2 <+112>:   mov    -0x408(%rbp),%rax
   0x00000000000009a9 <+119>:   mov    0xb4(%rax),%eax
   0x00000000000009af <+125>:   movslq %eax,%rdx
   0x00000000000009b2 <+128>:   lea    -0x400(%rbp),%rcx
   0x00000000000009b9 <+135>:   mov    -0x408(%rbp),%rax
   0x00000000000009c0 <+142>:   mov    %rcx,%rsi
   0x00000000000009c3 <+145>:   mov    %rax,%rdi
   0x00000000000009c6 <+148>:   callq  0x720 <strncpy@plt>
   ---> **strncpy(obj, msgbuf, obj->msg_len)** — length read from ***(obj + 0xb4)***; if **msg_len** is large (e.g. corrupted by username overflow), **strncpy** writes past the small inline message buffer → **heap overflow**.

   0x00000000000009cb <+153>:   leaveq
   0x00000000000009cc <+154>:   retq

End of assembler dump.
```
## `secret_backdoor`

```text
(gdb) disas secret_backdoor
   0x000000000000088c <+0>:     push   %rbp
   0x000000000000088d <+1>:     mov    %rsp,%rbp
   ---> Prologue.

   0x0000000000000890 <+4>:     add    $0xffffffffffffff80,%rsp
   ---> Allocate **128 bytes** (0x80) for local buffer.

   0x0000000000000894 <+8>:     mov    0x20171d(%rip),%rax        # 0x201fb8
   0x000000000000089b <+15>:    mov    (%rax),%rax
   ---> Load **stdin** (GOT → FILE* pointer, double dereference).

   0x000000000000089e <+18>:    mov    %rax,%rdx
   ---> Third argument: **rdx = stdin**.

   0x00000000000008a1 <+21>:    lea    -0x80(%rbp),%rax
   ---> Load address of local buffer (128 bytes at rbp-0x80).

   0x00000000000008a5 <+25>:    mov    $0x80,%esi
   ---> Second argument: **size = 128**.

   0x00000000000008aa <+30>:    mov    %rax,%rdi
   ---> First argument: **rdi = buffer**.

   0x00000000000008ad <+33>:    callq  0x770 <fgets@plt>
   ---> **fgets(buffer, 128, stdin)** — read a command from user.

   0x00000000000008b2 <+38>:    lea    -0x80(%rbp),%rax
   0x00000000000008b6 <+42>:    mov    %rax,%rdi
   ---> First argument: **rdi = buffer** (the string just read).

   0x00000000000008b9 <+45>:    callq  0x740 <system@plt>
   ---> **system(buffer)** — execute the user-supplied string as a shell command.

   0x00000000000008be <+50>:    leaveq 
   0x00000000000008bf <+51>:    retq   
   ---> Epilogue: return.

End of assembler dump.
```

**Exploitation note:** This function is **never called** by the program. It reads a string and passes it directly to `system()`. The exploit goal is to redirect execution here via the off-by-one overflow in `set_username` → corrupt `msg_len` → overflow in `set_msg` → overwrite saved RIP with the address of `secret_backdoor`.
