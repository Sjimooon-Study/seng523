lemma EquationFour(x: int)
    ensures 7 * x + 5 < (x + 3) * (x + 4)
{
    // (x + 3) * (x + 4) = power(x, 2) + 3 * x + 4 * x + 12 = power(x, 2) + 7 * x + 12
    calc {
        (x + 3) * (x + 4);
        == { assert (x + 3) * (x + 4) == power(x, 2) + 3 * x + 4 * x + 12; }
        power(x, 2) + 3 * x + 4 * x + 12;
        == { assert 3 * x + 4 * x == 7 * x; }
        power(x, 2) + 7 * x + 12;
    }

    // 7 * x + 5 < (x + 3) * (x + 4)
    calc {
        7 * x + 5 < power(x, 2) + 7 * x + 12;
        == { assert 5 < power(x, 2) + 12; }
        true;
    }
}

function power(a: int, b: int) : int
    requires b >= 0
    decreases b
{
    if b == 0 then 1
    else a * power(a, b - 1)
}
