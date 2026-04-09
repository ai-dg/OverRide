# XOR Cipher and Known-Plaintext Attack

## What is XOR?

XOR (exclusive or) is a bitwise operation: each output bit is 1 if the corresponding input bits differ, 0 if they're the same.

```
A ^ B = C
C ^ B = A    (XOR is its own inverse)
C ^ A = B
```

This reversibility makes XOR useful for simple encryption — but also trivially breakable when any two of the three values (plaintext, key, ciphertext) are known.

## XOR as a cipher

A single-byte XOR cipher encrypts each byte of the plaintext with the same key byte:

```c
for (i = 0; i < len; i++)
    ciphertext[i] = plaintext[i] ^ key;
```

To decrypt, apply the same XOR:

```c
for (i = 0; i < len; i++)
    plaintext[i] = ciphertext[i] ^ key;
```

## Known-plaintext attack

If the attacker knows both the ciphertext and the expected plaintext, recovering the key is trivial:

```
key = ciphertext[0] ^ plaintext[0]
```

One byte is enough to recover a single-byte key. For multi-byte keys, each position reveals one key byte.

## In this project (Level03)

- `decrypt()` XORs a 16-byte hardcoded buffer with a single-byte key
- The expected plaintext is `"Congratulations!"` (also hardcoded)
- Key recovery: `0x51 ^ 0x43 = 0x12 = 18`
- The key determines the input: `input = 0x1337d00d - 18 = 322424827`

## Why this is not real encryption

- Single-byte XOR has only 256 possible keys — brute-forceable in microseconds
- The expected plaintext is in the binary itself — classic known-plaintext scenario
- No key derivation, no salt, no IV — pure obfuscation

## References

- XOR cipher (Wikipedia): https://en.wikipedia.org/wiki/XOR_cipher
- Known-plaintext attack (Wikipedia): https://en.wikipedia.org/wiki/Known-plaintext_attack
- CWE-327 Use of a Broken or Risky Cryptographic Algorithm: https://cwe.mitre.org/data/definitions/327.html
