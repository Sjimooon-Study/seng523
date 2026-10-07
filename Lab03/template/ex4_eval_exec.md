The rules for both `eval()` and `exec()` are the same, as we for both are looking for non-constant/variable input arguments that could contain user input and be a security risk. The `pattern` will match any call to `eval()`/`exec()`, where any one of the arguments isn't a string literal, i.e. a hardcoded string that we can trust have the same value that we defined it to have in the code.

We specify the match for the variable argument in the `metavariable-pattern` with a `pattern-not` which will make `$ARG` match everything that is not a string literal.

In the commented out code, there's another approach. This works like a whitelist; we will report everything unless we specify that it's allowed. However, this approach will cause calls without any parameter to be reported as well. Which in principle is undesirable since we in that case don't pass any variable that could be risky.
