### vulnerable_applications/command_injection.py
This script allows for OS command injections. `os.system()` will run its argument in the system shell, so special characters like `&&` or `;`, which are commonly used in linux commands, let an attacker chain on their own commands. `variable1(cmd)` runs whatever command it is given directly. `variable2(user)` and `variable3(user)` build the command by inserting user input into a string, so we can do something like `user = "; rm -rf ~"`, which lets the attacker break out of our intended command. `constantstr()` is safe since the command is hardcoded.

Resources:
- https://docs.python.org/3/library/os.html#os.system
- https://owasp.org/www-community/attacks/Command_Injection


### vulnerable_applications/eval_exec.py
`my_eval()` returns the results from a single Python expression (calls `eval()`). `my_exec()` execute some block of Python code (calls `exec()`). Both of these can be risky since they will allow a potential attacker to do remote code execution. The evaluated expression (or expressions in `exec()`) will be executed in the current scope, which means an attacker will have access to other variables visible from that scope and can influence the entirety of that scope. An attacker will also be able to "break out of the Python script" and execute system commands with this expression: `__import__('os').system(...)`

`my_lateral()` should be safe since the expression is a hardcoded string. However, instead we should just write the expression as actual code, since using `eval()` here is unnecessary and inefficient.

Resources:
- https://safeguard.sh/resources/blog/code-injection-prevention-python

### vulnerable_applications/subprocess_popen.py
`subprocess.Popen()` is attack vector for shell injection, since it can be used to execute commands on the system running the Python script. Calling `subprocess.Popen()` with `shell=True` opens the user chosen shell (bash, fish, zsh, etc. on Linux) and allows the usage of shell features (pipes, filename wildcards, environment variables, etc.). While more powerful, this can be risky combined with untrusted (tainted) inputs. Additionally, you must use syntax that is understood by the given shell, which can cause compatibility issues when the shell type used by the user isn't taken into account in the Python script. It's therefore strongly recommended to leave the `shell` parameter at its default value of `False` when possible (for security and compatibility). The same applies to `subprocess.run()` as it calls `subprocess.Popen()` internally.

Resources:
- https://docs.python.org/3/library/subprocess.html
- https://docs.python.org/2/library/subprocess.html#frequently-used-arguments

### vulnerable_applications/path_traversal.py
