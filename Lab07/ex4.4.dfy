function SumUpTo(n: nat): nat
  ensures SumUpTo(n) == n * (n + 1) / 2
  decreases n
{
  if n == 0 then 0 else n + SumUpTo(n - 1)
}


method Main(args: seq<string>)
{
  var rArgs := args;
  if |rArgs| > 0 && rArgs[0] == "dotnet" {
    rArgs := rArgs[1..];
  }

  if |rArgs| < 1 {
    print "Usage: sumupto <n>\n";
    return;
  }

  var nInt := ParseInt(rArgs[0]);

  if nInt < 0 {
    print "Error: n must be nonnegative.\n";
    return;
  }

  var n := nInt as nat;   // safe because we checked nInt >= 0

  var s := SumUpTo(n);
  print s, "\n";
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
