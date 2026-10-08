The original template used `pattern: os.system(...)`, which flags every call to `os.system()`, including the safe `constantstr()` call.

I replaced it with a `patterns` block, so matches only when all sub-patterns match. `os.system(...)` matches every call, since `...` without quotes means any expression. `pattern-not: os.system("...")` then removes calls whose argument is a string literal. I also changed the rule's id and message to match our case of detecting a variable.

The results on `command_injection.py`:
- Line 4 (`"echo hello"`) is not flagged since it's a plain literal
- Line 7 is flagged since the argument is a variable
- Line 10 is flagged since it's a string concatenated with a variable (not a single literal)
- Line 13 is flagged since semgrep doesn't treat an f-string containing the variable `{user}` as a plain literal

Our goal was to cut down on false positives. A constant argument won't come from a user, so it won't allow for command injection. There's only danger when user input is inserted into the command, so the rule now only warns where a user can control what's ran. 
