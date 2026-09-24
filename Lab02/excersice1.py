# Example for requirement 1
def myfunction(a, b):
     c = a + 20 - b # <-- c is defined,
     d = a # but never used
     e = b
     return d, e
# Example for requirement 2
def outiefunc (a, b):
     c = 30 # <--c is defined, but not used
     d = a + b
     def inniefunc(x, y):
          c = 15 # <--this is a different c!
          return c
     return d


# Example for requirement 3
def outiefunc (a, b):
     c = 30 # <-- c is defined here...
     d = a + b
     def inniefunc(x, y):
          retval = c*2 # <-- ...and used here
          return retval
     return d

# Example for requirement 4
def myfunction(a, b):
     x = 20 # <-- outer x
     def myotherfunction():
          x = 10 # <-- inner x aliases outer x