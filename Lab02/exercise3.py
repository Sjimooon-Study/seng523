# Example 1 – not constant vs constant
def myfunction(a, b):
  if a != 0:
    print("Nonzero")

# Example 2 – not constant
def myfunction(a, b):
  if a:
    print("a")

# Example 3 – constant
def myfunction(a, b):
  if "hello":
    print("Hello")

# Example 4 – constant vs constant
def myfunction(a, b):
  if 0 == 0:
    print("Yep, still zero")