method Mul(a: int, b: int) returns (prod: int)
  requires b >= 0
{
  var i := 0;
  prod := 0;
  while i < b
    invariant 0 <= i <= b
    invariant prod == a * i
    decreases b - i
  {
    prod := prod + a;
    i := i + 1;
  }

  assert prod == a * b;
}
