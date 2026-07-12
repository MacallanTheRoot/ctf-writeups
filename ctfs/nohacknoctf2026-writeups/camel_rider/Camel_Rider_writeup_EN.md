# NoHackNoCTF 2026 — Camel Rider Writeup

- **Author:** Efe Şahinbaş
- **GitHub Repository:** [MacallanTheRoot/ctf-writeups](https://github.com/MacallanTheRoot/ctf-writeups/)

**Category:** Jail / Sandbox Escape  
**Challenge:** Camel Rider  
**Hint:** `flag.txt`  
**Goal:** Read the contents of `flag.txt` from a restricted Perl environment.

---

## Summary

Camel Rider was a Perl jail challenge. The remote service accepted user input and evaluated it as Perl code, but common file-reading and command-execution primitives were filtered. Direct attempts using functions such as `open`, `read`, `sysread`, `system`, `exec`, `eval`, `readpipe`, and `do` were blocked by the jail and returned the filter response.

The intended bypass was not to call `open` directly. Instead, the solution abuses Perl's diamond operator, `<>`, together with the special `@ARGV` array. By setting `@ARGV` to contain `flag.txt`, Perl implicitly treats that value as an input file and opens it internally when `<>` is evaluated.

Final payload:

```perl
BEGIN{@ARGV=(q{flag.txt}); print <>}
```

Flag:

```text
NHNC{Jf8fnibf7fhiqfwbqubFmoyt4191qv3rH}
```

---

## 1. Initial Analysis

After connecting to the service, the challenge behaved like a restricted Perl interpreter. The prompt accepted a line of Perl code, executed it, and returned the output.

Since the hint was simply:

```text
flag.txt
```

The first objective was clear: find a way to read `flag.txt` from inside the jail.

The obvious Perl approaches were blocked:

```perl
open my $fh, '<', 'flag.txt'; print <$fh>;
```

```perl
print `cat flag.txt`;
```

```perl
system('cat flag.txt');
```

Inputs containing dangerous keywords triggered the filter. The jail responded with something like:

```text
Meow
```

and closed or interrupted the session.

This suggested that the challenge was not about finding the filename, but about finding a Perl language feature that could perform file access without using the forbidden words directly.

---

## 2. Understanding the Restriction

The filter appeared to block common file I/O and command-execution primitives, including names such as:

```text
open
read
sysread
system
exec
eval
readpipe
do
```

Typical bypass attempts were not reliable either. Building function names dynamically, using substitution tricks, or trying indirect invocation was either blocked or restricted by the runtime environment.

At this point, the important observation was that Perl has several implicit behaviors. Not every file read requires an explicit call to `open` in the user's code.

The useful primitive here was the diamond operator:

```perl
<>
```

---

## 3. Perl's Diamond Operator

In Perl, the diamond operator is commonly used to read input line by line.

For example:

```perl
while (<>) {
    print $_;
}
```

When used without an explicit filehandle, `<>` reads from files listed in the special `@ARGV` array. If `@ARGV` contains filenames, Perl internally opens those files and reads from them. If `@ARGV` is empty, it reads from standard input.

This behavior is the key to the challenge.

We do not need to write:

```perl
open(...)
```

Instead, we can set:

```perl
@ARGV = ('flag.txt');
```

and then evaluate:

```perl
<>
```

Perl will implicitly open and read `flag.txt` through the diamond operator.

---

## 4. Building the Payload

The minimal idea is:

```perl
@ARGV=('flag.txt'); print <>
```

However, wrapping it in a `BEGIN` block makes the payload cleaner in a jail context.

```perl
BEGIN{@ARGV=(q{flag.txt}); print <>}
```

Breakdown:

```perl
BEGIN { ... }
```

Runs the block as soon as the code is compiled. This is useful in restricted interpreters because it executes the relevant logic immediately.

```perl
@ARGV=(q{flag.txt})
```

Sets Perl's argument list to contain the target filename. `q{...}` is Perl's single-quote-like quoting operator, so this avoids needing normal quotes.

```perl
print <>
```

Uses the diamond operator. Since `@ARGV` contains `flag.txt`, Perl implicitly reads from that file and prints its content.

---

## 5. Exploit

Final payload:

```perl
BEGIN{@ARGV=(q{flag.txt}); print <>}
```

When submitted to the service, the interpreter reads `flag.txt` through the implicit `@ARGV` mechanism and prints the flag.

---

## 6. Flag

```text
NHNC{Jf8fnibf7fhiqfwbqubFmoyt4191qv3rH}
```

---

## Root Cause

The jail attempted to prevent file access by filtering explicit dangerous keywords such as `open`, `read`, and command-execution functions. However, it did not account for Perl's implicit file-reading behavior through the diamond operator and `@ARGV`.

This allowed file access without directly writing a blocked file I/O function name.

---

## Mitigation

For a real sandbox, keyword filtering is not a safe security model. Perl has many implicit behaviors, special variables, and alternate syntax forms that can bypass simple string checks.

Safer approaches include:

1. Do not evaluate raw user-controlled Perl code.
2. Run untrusted code inside a strongly isolated container or VM.
3. Remove filesystem access at the OS level.
4. Use seccomp/AppArmor/SELinux-style restrictions where possible.
5. Avoid relying on denylist-based keyword filtering.
6. Use an allowlist-based parser if the task requires evaluating a small subset of a language.

---

## Final Notes

This was a compact Perl jail challenge. The trick was recognizing that the blocked operation did not need to be called directly. By abusing `@ARGV` and `<>`, the interpreter itself performed the file read.

Final answer:

```text
NHNC{Jf8fnibf7fhiqfwbqubFmoyt4191qv3rH}
```
