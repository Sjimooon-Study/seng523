### vulnerable_applications/command_injection.py
This script allows for OS command injections. `os.system()` will run its argument in the system shell, so special characters like `&&` or `;`, which are commonly used in linux commands, let an attacker chain on their own commands. `variable1(cmd)` runs whatever command it is given directly. `variable2(user)` and `variable3(user)` build the command by inserting user input into a string, so we can do something like `user = "; rm -rf ~"`, which lets the attacker break out of our intended command. `constantstr()` is safe since the command is hardcoded and doesn't allow for user input. 

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
The `open()` function follows the given path and reads the bytes of that file, letting you read its contents. With a relative path, the input can include something like `"uploads/" + "../"`, which means the incoming input can go outside of the intended scope. In this script, the functions that let the user input whatever path they want are `opener()`, `opener_concat()` and `opener_join_var()`. `opener_join_varconst()` forces the ending `/downloads`, which is a small sanitization, but the user can still go to another user's downloads folder. `opener_const_concat()` and `opener_join_const()` are safe because the path is hardcoded. This can be very vulnerable if the system does not have a permission-based system, because a low-level user could then go into every file, such as our database files and passwords. They could leak all the files of the system, and by reading different files, they could discover other vulnerabilities in our own system. To prevent this, the important thing is to have a filter that only allows certain user input, or a blacklist of keywords like `../`, to stop the user from going outside of the desired scope.

Resources:
- https://docs.python.org/3/library/functions.html#open
