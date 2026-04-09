# Integer Overflow

## What is it?

An integer overflow occurs when an arithmetic operation produces a value that exceeds the maximum (or minimum) value the data type can hold. In C, unsigned integers wrap around silently: `UINT_MAX + 1 = 0`.

On 32-bit systems, `unsigned int` holds values from 0 to 4,294,967,295 (2^32 - 1). Any result above this wraps modulo 2^32.

## Why it matters for exploitation

When a program uses an index to compute a memory address (e.g., `array[index]` which becomes `base + index * 4`), an integer overflow in the multiplication can make a large index point to the same memory as a small one:

```
Normal:    114 * 4 = 456
Overflow:  1073741938 * 4 = 4294967752 → mod 2^32 = 456
```

Both indices access the same memory location, but they have different values for other checks (like `index % 3`).

## The bypass pattern

If a program filters certain index values (e.g., rejects `index % 3 == 0`), the attacker can find an equivalent index that passes the filter:

```
target_offset = desired_index * 4
N = desired_index + k * 2^30    (for k = 1, 2, ...)

Check: N * 4 mod 2^32 == target_offset  ✓
Check: N % 3 != 0                       ✓ (try different k values)
```

## In this project (Level07)

- `store_number` rejects indices where `index % 3 == 0`
- We need to write to index 114 (saved EIP), but `114 % 3 == 0`
- Solution: use `1073741938` (= 114 + 2^30)
  - `1073741938 * 4 = 4294967752`, mod 2^32 = 456 = `114 * 4` ✓
  - `1073741938 % 3 = 1` ≠ 0 ✓

## How to prevent it

- Always validate that indices are within array bounds (`0 <= index < size`)
- Use `size_t` for sizes and check for overflow before multiplication
- Enable compiler warnings: `-ftrapv` (traps on signed overflow)

## References

- CWE-190 Integer Overflow or Wraparound: https://cwe.mitre.org/data/definitions/190.html
- Integer overflow (Wikipedia): https://en.wikipedia.org/wiki/Integer_overflow
- CERT C Coding Standard — INT32-C: https://wiki.sei.cmu.edu/confluence/display/c/INT32-C.+Ensure+that+operations+on+signed+integers+do+not+result+in+overflow
