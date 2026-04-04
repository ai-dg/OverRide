# level02 — `main` (x86-64, GDB)

Each line below is the GDB `disas` output with an English note for exploitation / control flow.

```text
(gdb) disas main
Dump of assembler code for function main:
   0x0000000000400814 <+0>:     push   %rbp
   ---> Prologue: save frame pointer (64-bit).

   0x0000000000400815 <+1>:     mov    %rsp,%rbp
   ---> Establish stack frame; locals below %rbp.

   0x0000000000400818 <+4>:     sub    $0x120,%rsp
   ---> Allocate 0x120 bytes: username line, password line, pass file buffer, FILE*, count.

   0x000000000040081f <+11>:    mov    %edi,-0x114(%rbp)
   ---> Save argc (unused later for auth logic).

   0x0000000000400825 <+17>:    mov    %rsi,-0x120(%rbp)
   ---> Save argv (unused for core login path).

   0x000000000040082c <+24>:    lea    -0x70(%rbp),%rdx
   ---> Address of first big stack buffer (username line, ~0x70 bytes region).

   0x0000000000400830 <+28>:    mov    $0x0,%eax
   0x0000000000400835 <+33>:    mov    $0xc,%ecx
   0x000000000040083a <+38>:    mov    %rdx,%rdi
   0x000000000040083d <+41>:    rep stos %rax,%es:(%rdi)
   ---> Zero 12×8 = 96 bytes with stosq (clear username buffer area).

   0x0000000000400840 <+44>:    mov    %rdi,%rdx
   0x0000000000400843 <+47>:    mov    %eax,(%rdx)
   0x0000000000400845 <+49>:    add    $0x4,%rdx
   ---> Finish clearing tail / align remaining dword (compiler-generated spill).

   0x0000000000400849 <+53>:    lea    -0xa0(%rbp),%rdx
   ---> Address of 41-byte password-file buffer (0x29 bytes used logically).

   0x0000000000400850 <+60>:    mov    $0x0,%eax
   0x0000000000400855 <+65>:    mov    $0x5,%ecx
   0x000000000040085a <+70>:    mov    %rdx,%rdi
   0x000000000040085d <+73>:    rep stos %rax,%es:(%rdi)
   ---> Zero 5×8 = 40 bytes + next instructions clear rest.

   0x0000000000400860 <+76>:    mov    %rdi,%rdx
   0x0000000000400863 <+79>:    mov    %al,(%rdx)
   0x0000000000400865 <+81>:    add    $0x1,%rdx
   ---> Clear final byte / padding of pass buffer.

   0x0000000000400869 <+85>:    lea    -0x110(%rbp),%rdx
   ---> Address of password input line buffer (second fgets).

   0x0000000000400870 <+92>:    mov    $0x0,%eax
   0x0000000000400875 <+97>:    mov    $0xc,%ecx
   0x000000000040087a <+102>:   mov    %rdx,%rdi
   0x000000000040087d <+105>:   rep stos %rax,%es:(%rdi)
   ---> Zero password input buffer (similar size to username).

   0x0000000000400880 <+108>:   mov    %rdi,%rdx
   0x0000000000400883 <+111>:   mov    %eax,(%rdx)
   0x0000000000400885 <+113>:   add    $0x4,%rdx
   ---> Trailing clear for password buffer.

   0x0000000000400889 <+117>:   movq   $0x0,-0x8(%rbp)
   ---> FILE* / handle for fopen initialized to NULL.

   0x0000000000400891 <+125>:   movl   $0x0,-0xc(%rbp)
   ---> fread byte count stored here (must be 0x29 later).

   0x0000000000400898 <+132>:   mov    $0x400bb0,%edx
   0x000000000040089d <+137>:   mov    $0x400bb2,%eax
   ---> Pointers to "rb" mode string for fopen (split across two rodata labels).

   0x00000000004008a2 <+142>:   mov    %rdx,%rsi
   ---> fopen path string (first arg in 64-bit: %rdi will be path).

   0x00000000004008a5 <+145>:   mov    %rax,%rdi
   ---> Actually mov path to %rdi — check: edx/eax are path and mode; rsi/rdi setup for fopen(path, mode).

   0x00000000004008a8 <+148>:   callq  0x400700 <fopen@plt>
   ---> Open `/home/users/level03/.pass` (or similar) for reading binary password.

   0x00000000004008ad <+153>:   mov    %rax,-0x8(%rbp)
   ---> Save FILE*.

   0x00000000004008b1 <+157>:   cmpq   $0x0,-0x8(%rbp)
   0x00000000004008b6 <+162>:   jne    0x4008e6 <main+210>
   ---> If fopen succeeded, skip error exit.

   0x00000000004008b8 <+164>:   mov    0x200991(%rip),%rax        # stderr
   0x00000000004008bf <+171>:   mov    %rax,%rdx
   ---> Load stderr for fwrite.

   0x00000000004008c2 <+174>:   mov    $0x400bd0,%eax
   ---> Pointer to error message string (open failure).

   0x00000000004008c7 <+179>:   mov    %rdx,%rcx
   0x00000000004008ca <+182>:   mov    $0x24,%edx
   0x00000000004008cf <+187>:   mov    $0x1,%esi
   0x00000000004008d4 <+192>:   mov    %rax,%rdi
   0x00000000004008d7 <+195>:   callq  0x400720 <fwrite@plt>
   ---> fwrite error banner to stderr (36 bytes = 0x24).

   0x00000000004008dc <+200>:   mov    $0x1,%edi
   0x00000000004008e1 <+205>:   callq  0x400710 <exit@plt>
   ---> exit(1) on fopen failure.

   0x00000000004008e6 <+210>:   lea    -0xa0(%rbp),%rax
   ---> Buffer address for fread destination.

   0x00000000004008ed <+217>:   mov    -0x8(%rbp),%rdx
   ---> FILE* into %rcx/%rdx for fread signature.

   0x00000000004008f1 <+221>:   mov    %rdx,%rcx
   ---> Third arg: FILE* (calling convention uses rcx for 4th in some layouts — here fread setup).

   0x00000000004008f4 <+224>:   mov    $0x29,%edx
   ---> Read count = 41 bytes (exact .pass length).

   0x00000000004008f9 <+229>:   mov    $0x1,%esi
   ---> Element size 1.

   0x00000000004008fe <+234>:   mov    %rax,%rdi
   ---> Buffer pointer first arg.

   0x0000000000400901 <+237>:   callq  0x400690 <fread@plt>
   ---> Read password file into stack buffer.

   0x0000000000400906 <+242>:   mov    %eax,-0xc(%rbp)
   ---> Store number of bytes read (must equal 0x29).

   0x0000000000400909 <+245>:   lea    -0xa0(%rbp),%rax
   0x0000000000400910 <+252>:   mov    $0x400bf5,%esi
   ---> Address of "\n" string for strcspn (strip newline).

   0x0000000000400915 <+257>:   mov    %rax,%rdi
   0x0000000000400918 <+260>:   callq  0x4006d0 <strcspn@plt>
   ---> Find first newline index in file buffer.

   0x000000000040091d <+265>:   movb   $0x0,-0xa0(%rbp,%rax,1)
   ---> NUL-terminate password string at newline.

   0x0000000000400925 <+273>:   cmpl   $0x29,-0xc(%rbp)
   0x0000000000400929 <+277>:   je     0x40097d <main+361>
   ---> If fread returned exactly 41 bytes, continue to UI; else error path.

   0x000000000040092b <+279>:   mov    0x20091e(%rip),%rax        # stderr
   ... (fwrite error “failed to read password file” ×2)
   0x0000000000400978 <+356>:   callq  0x400710 <exit@plt>
   ---> exit(1) if read size wrong.

   0x000000000040097d <+361>:   mov    -0x8(%rbp),%rax
   0x0000000000400981 <+365>:   mov    %rax,%rdi
   0x0000000000400984 <+368>:   callq  0x4006a0 <fclose@plt>
   ---> fclose after successful read (password now only in memory).

   0x0000000000400989 <+373>:   mov    $0x400c20,%edi
   ... puts ×4
   ---> Print login banner lines.

   0x00000000004009b1 <+413>:   mov    $0x400cd9,%eax
   0x00000000004009b6 <+418>:   mov    %rax,%rdi
   0x00000000004009b9 <+421>:   mov    $0x0,%eax
   0x00000000004009be <+426>:   callq  0x4006c0 <printf@plt>
   ---> printf("--[ Username: ") style prompt.

   0x00000000004009c3 <+431>:   mov    0x20087e(%rip),%rax        # stdin
   0x00000000004009ca <+438>:   mov    %rax,%rdx
   0x00000000004009cd <+441>:   lea    -0x70(%rbp),%rax
   0x00000000004009d1 <+445>:   mov    $0x64,%esi
   0x00000000004009d6 <+450>:   mov    %rax,%rdi
   0x00000000004009d9 <+453>:   callq  0x4006f0 <fgets@plt>
   ---> Read username (max 100 chars).

   0x00000000004009de <+458>:   lea    -0x70(%rbp),%rax
   0x00000000004009e2 <+462>:   mov    $0x400bf5,%esi
   0x00000000004009e7 <+467>:   mov    %rax,%rdi
   0x00000000004009ea <+470>:   callq  0x4006d0 <strcspn@plt>
   0x00000000004009ef <+475>:   movb   $0x0,-0x70(%rbp,%rax,1)
   ---> Strip newline from username.

   0x00000000004009f4 <+480>:   mov    $0x400ce8,%eax
   ... printf password prompt
   0x0000000000400a01 <+493>:   callq  0x4006c0 <printf@plt>
   ---> printf("--[ Password: ").

   0x0000000000400a06 <+498>:   mov    0x20083b(%rip),%rax        # stdin
   0x0000000000400a0d <+505>:   mov    %rax,%rdx
   0x0000000000400a10 <+508>:   lea    -0x110(%rbp),%rax
   0x0000000000400a17 <+515>:   mov    $0x64,%esi
   0x0000000000400a1c <+520>:   mov    %rax,%rdi
   0x0000000000400a1f <+523>:   callq  0x4006f0 <fgets@plt>
   ---> Read typed “password” line.

   0x0000000000400a24 <+528>:   lea    -0x110(%rbp),%rax
   0x0000000000400a2b <+535>:   mov    $0x400bf5,%esi
   0x0000000000400a30 <+540>:   mov    %rax,%rdi
   0x0000000000400a33 <+543>:   callq  0x4006d0 <strcspn@plt>
   0x0000000000400a38 <+548>:   movb   $0x0,-0x110(%rbp,%rax,1)
   ---> Strip newline from typed password.

   0x0000000000400a40 <+556>:   mov    $0x400cf8,%edi
   0x0000000000400a45 <+561>:   callq  0x400680 <puts@plt>
   ---> Separator line before compare.

   0x0000000000400a4a <+566>:   lea    -0x110(%rbp),%rcx
   0x0000000000400a51 <+573>:   lea    -0xa0(%rbp),%rax
   0x0000000000400a58 <+580>:   mov    $0x29,%edx
   0x0000000000400a5d <+585>:   mov    %rcx,%rsi
   0x0000000000400a60 <+588>:   mov    %rax,%rdi
   0x0000000000400a63 <+591>:   callq  0x400670 <strncmp@plt>
   ---> Compare first 0x29 bytes: file password vs typed line (timing / length leak possible).

   0x0000000000400a68 <+596>:   test   %eax,%eax
   0x0000000000400a6a <+598>:   jne    0x400a96 <main+642>
   ---> If mismatch, go to failure path.

   0x0000000000400a6c <+600>:   mov    $0x400d22,%eax
   0x0000000000400a71 <+605>:   lea    -0x70(%rbp),%rdx
   0x0000000000400a75 <+609>:   mov    %rdx,%rsi
   0x0000000000400a78 <+612>:   mov    %rax,%rdi
   0x0000000000400a7b <+615>:   mov    $0x0,%eax
   0x0000000000400a80 <+620>:   callq  0x4006c0 <printf@plt>
   ---> Success: printf("Greetings, %s!\n", username) — **format string if username contains %**.

   0x0000000000400a85 <+625>:   mov    $0x400d32,%edi
   0x0000000000400a8a <+630>:   callq  0x4006b0 <system@plt>
   ---> system("/bin/sh") on success.

   0x0000000000400a8f <+635>:   mov    $0x0,%eax
   0x0000000000400a94 <+640>:   leaveq
   0x0000000000400a95 <+641>:   retq
   ---> Return 0 from main.

   0x0000000000400a96 <+642>:   lea    -0x70(%rbp),%rax
   0x0000000000400a9a <+646>:   mov    %rax,%rdi
   0x0000000000400a9d <+649>:   mov    $0x0,%eax
   0x0000000000400aa2 <+654>:   callq  0x4006c0 <printf@plt>
   ---> Failure: printf(username) — **classic format-string primitive** (no format string).

   0x0000000000400aa7 <+659>:   mov    $0x400d3a,%edi
   0x0000000000400aac <+664>:   callq  0x400680 <puts@plt>
   ---> puts(" does not have access!").

   0x0000000000400ab1 <+669>:   mov    $0x1,%edi
   0x0000000000400ab6 <+674>:   callq  0x400710 <exit@plt>
   ---> exit(1).

End of assembler dump.
```

**Key exploitation anchors:** `strncmp` length 0x29; **printf(username)** on failure path; **printf("Greetings, %s!", …)** on success — both are format-string sinks if username is controlled.
