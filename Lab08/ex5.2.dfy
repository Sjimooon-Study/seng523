method SumOdd(n: int) returns (sum: int)
  requires n >= 0
{
  var i := 0;
  sum := 0;
  while i < n
    invariant 0 <= i <= n
    invariant sum == i * i
    decreases n - i
  {
    sum := sum + (2 * i + 1);
    i := i + 1;
  }
  assert sum == n * n;
}
