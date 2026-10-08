We use two rules, one for `open()` and one for `os.path.join()`, since a path can either be passed straight to `open()` or with `os.path.join()`.

The first rule matches any call `open($ARG, ...)`, where `$ARG` is the path and `...` allows other arguments like the mode. A `metavariable-pattern` with `pattern-not: '"..."'` then removes the calls where the path is a string literal, so only variable or mixed paths (like `"uploads/" + user`) are reported.

The second rule matches `os.path.join(..., $ARG, ...)`, so `$ARG` can be any argument in the call. With the same `metavariable-pattern`, the call is reported if at least one argument is not a string literal, since a single user-controlled part like `"../"` is enough to change the whole path. `os.path.join("home", "myfiles")` is therefore not reported.
