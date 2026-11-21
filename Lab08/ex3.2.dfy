lemma EquationTwo(x: int, y: int)
    ensures 5 * x - 3 * (y + x) == 2 * x - 3 * y
{
    // 5 * x - 3 * (y + x) = 5 * x - 3 * y - 3 * x = 2 * x - 3 * y
    calc {
        5 * x - 3 * (y + x);
        == { assert -3 * (y + x) == -3 * y - 3 * x; }
        5 * x - 3 * y - 3 * x;
        == { assert 5 * x - 3 * x == 2 * x; }
        2 * x - 3 * y;
    }
}
