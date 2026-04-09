# Symlink Attack and Setuid Abuse

## What is a symbolic link?

A symbolic link (symlink) is a special file that points to another file or directory. When a program opens a symlink, the OS transparently follows it to the target file. The program sees the target's content, not the symlink itself.

```bash
ln -sf /etc/shadow mylink
cat mylink    # reads /etc/shadow (if permissions allow)
```

## What is a setuid binary?

A setuid binary runs with the permissions of its **owner**, not the user who executes it. If `level08` is owned by `level09` and has the setuid bit, any user running `level08` temporarily gains `level09`'s file access rights.

```
-rwsr-s--- 1 level09 users 12975 level08
 ^^^
 setuid bit
```

## The attack

When a setuid binary opens a file specified by the user (e.g., `argv[1]`), it reads the file with elevated privileges. If the program then writes the content to a location the attacker can read, the attacker effectively escalates their access.

### The path problem

If the program builds an output path like `./backups/<argv[1]>`, passing a full path like `/home/users/level09/.pass` creates `./backups//home/users/level09/.pass` — the nested directories don't exist, so the write fails.

### The symlink solution

Create a symlink with a simple name:

```bash
ln -sf /home/users/level09/.pass token
```

Now:
- `fopen("token", "r")` → follows symlink → reads `/home/users/level09/.pass` (setuid privileges)
- `open("./backups/token", ...)` → flat path → file creation succeeds
- Content is copied → password is now in a readable local file

## In this project (Level08)

- `level08` is setuid `level09`
- It reads `argv[1]` and copies its content to `./backups/<argv[1]>`
- The `strcpy` in `log_wrapper` is protected by a stack canary → no memory corruption
- The real vulnerability is the unchecked file path combined with setuid privileges
- A symlink named `token` pointing to `.pass` bypasses the path issue

## How to prevent it

- Check the real path of files with `realpath()` before opening
- Drop privileges before opening user-specified files (`seteuid(getuid())`)
- Use `O_NOFOLLOW` flag to reject symlinks
- Validate that the target file is within an allowed directory

## References

- CWE-59 Improper Link Resolution Before File Access: https://cwe.mitre.org/data/definitions/59.html
- Symlink race (Wikipedia): https://en.wikipedia.org/wiki/Symlink_race
- setuid (Linux man page): https://man7.org/linux/man-pages/man2/setuid.2.html
