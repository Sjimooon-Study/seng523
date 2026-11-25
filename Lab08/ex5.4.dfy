method ReachN(n: int) returns (i: int)
  requires n >= 0
{
  i := 0;
  while i < n
    invariant 0 <= i <= n
    decreases n - i
  {
    i := i + 1;
  }

  assert i == n;
}