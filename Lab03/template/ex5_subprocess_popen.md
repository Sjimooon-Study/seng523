We specifiy two main patterns, to detect calls to either `subprocess.Popen()` or `subprocess.run()` with `shell=True`. To not repeat and have two copies of the same configuration for both `Popen` and `run`, a `metavariable-regex` pattern is used to do a RegEx match for both of those names. This is an exact match from start (^) to end ($). The metavariable `$FUNC` can then be placed in the other patterns to search for either of the two function names.

As the two functions can be called with either a single argument or an array of arguments, we are searching for *either* of them with `pattern-either`.

The first child pattern matches calls with a single argument (and of course the risky `shell=True` parameter). Here we also exclude all the array matches with a `pattern-not` pattern. A `metavariable-pattern` is used to not match string literal arguments. Note the use of the single quotes around the ellipsis operator for string literals (`"..."`) to make semgrep read the YAML string as `"..."` and not just `...`. 

The second child pattern matches all the array arguments. Using the same `metavariable-pattern`, there will be a match when an argument in the array (followed by and preceded zero or more elements) is not a string literal, i.e. a variable, which is risky pared with `shell=True`.

The third and fourth pattern are like the first and second respectively, but will catch cases where the argument is passed using the parameter name `args`.

In all patterns, we make it so `shell=True` doesn't have to be the last argument, by adding the ellipsis after it in the patterns. It can be preceded zero or more other arguments. We also ellipsies between the argument and `shell=True`, so that they don't have to be exactly next to each other. 
