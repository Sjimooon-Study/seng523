function Bump(n: int): int
{
  if n <= 0 then 1 else Bump(n - 1) + 1
}


lemma {:induction false} BumpGreater(n: int)
  ensures Bump(n) > n
  decreases n
{
  if n <= 0 {
    //base case: Bump(n) == 1 and n <= 0 so Bump(n) > n
    calc {
      Bump(n);
    == { assert n <= 0; }
      1;
    >  { assert n <= 0; }
      n;
    }
  } else {
    //the innductive step: assume BumpGreater(n-1). ie. Bump(n-1) > n-1
    calc {
      Bump(n);
    == { assert n > 0; }
      Bump(n - 1) + 1;
    >  { BumpGreater(n - 1);
         assert Bump(n - 1) > n - 1; }
      (n - 1) + 1;
    ==
      n;
    }
  }
}


method ExampleLemmaUse(a: int) {
    var b := Bump(a);
    BumpGreater(a);   //a < Bump(a) == b
    var c := Bump(b);
    BumpGreater(b);   // b < Bump(b) == c
    //a < b < c over ints, so c - a >= 2
    assert 2 <= c - a;
}


method Main(args: seq<string>)
{
  var realArgs := args;
  if |realArgs| > 0 && realArgs[0] == "dotnet" {
    realArgs := realArgs[1..];
  }

  if |realArgs| < 1 {
    print "Usage: ex1.1_solution <x>\n";
    return;
  }

  var x := ParseInt(realArgs[0]);
  var r := Bump(x);
  print r, "\n";
}


method ParseInt(s: string) returns (n: int)
{
  var i := 0;
  var sign := 1;
  n := 0;

  if |s| == 0 {
    return;
  }

  if s[0] == '-' {
    sign := -1;
    i := 1;
  } else if s[0] == '+' {
    i := 1;
  }

  while i < |s|
  {
    var c := s[i] as int;
    var d := c - ('0' as int);

    if d < 0 || d > 9 {
      n := 0;
      return;
    }

    n := n * 10 + d;
    i := i + 1;
  }

  n := sign * n;
}
