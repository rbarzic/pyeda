"""
Test expression Boolean functions
"""

import sys

from pyeda.expr import (
    factor, simplify,
    var,
    Or, And, Not, Xor, Xnor, Equal, Implies, ITE,
    Nor, Nand, OneHot0, OneHot,
    f_not, f_or, f_nor, f_and, f_nand, f_xor, f_xnor, f_equal, f_implies, f_ite
)
from pyeda.vexpr import bitvec

import nose

MAJOR = sys.version_info.major
MINOR = sys.version_info.minor

a, b, c, d, e, p, q, s = map(var, 'abcdepqs')
X = bitvec('x', 16)
Y = bitvec('y', 16, 16, 16)

def test_ops():
    # __sub__, __rsub__
    assert (a - 0) == 1
    assert (0 - a) == -a
    assert (a - 1) == a
    assert (1 - a) == 1
    assert (a - b).equivalent(a + -b)
    # xor, equal, ite
    assert a.xor(b, c).equivalent(-a * -b * c + -a * b * -c + a * -b * -c + a * b * c)
    assert a.equal(b, c).equivalent(-a * -b * -c + a * b * c)
    assert s.ite(a, b).equivalent(s * a + -s * b)

def test_factor():
    assert factor(0) == 0
    assert factor(Implies(p, q)).equivalent(-p + q)
    assert factor(Xor(a, b)).equivalent(-a * b + a * -b)

def test_simplify():
    assert simplify(0) == 0
    assert simplify(And(1, 1, 1, 0, simplify=False)) == 0
    assert simplify(Or(0, 0, 0, 1, simplify=False)) == 1

    f1 = And(a, And(b, And(c, 0, simplify=False), simplify=False), simplify=False)
    f2 = Or(a, Or(b, Or(c, 1, simplify=False), simplify=False), simplify=False)
    if MAJOR >= 3:
        assert str(f1) == "a * b * c * 0"
        assert str(f2) == "a + b + c + 1"
    assert simplify(f1) == 0
    assert simplify(f2) == 1

def test_onehot0():
    assert OneHot0(0, 0, 0) == 1
    assert OneHot0(0, 0, 1) == 1
    assert OneHot0(0, 1, 0) == 1
    assert OneHot0(0, 1, 1) == 0
    assert OneHot0(1, 0, 0) == 1
    assert OneHot0(1, 0, 1) == 0
    assert OneHot0(1, 1, 0) == 0
    assert OneHot0(1, 1, 1) == 0

    assert OneHot0(a, b, c).equivalent((-a + -b) * (-a + -c) * (-b + -c))

def test_onehot():
    assert OneHot(0, 0, 0) == 0
    assert OneHot(0, 0, 1) == 1
    assert OneHot(0, 1, 0) == 1
    assert OneHot(0, 1, 1) == 0
    assert OneHot(1, 0, 0) == 1
    assert OneHot(1, 0, 1) == 0
    assert OneHot(1, 1, 0) == 0
    assert OneHot(1, 1, 1) == 0

    assert OneHot(a, b, c).equivalent((-a + -b) * (-a + -c) * (-b + -c) * (a + b + c))

def test_var():
    # Function
    assert a.support == {a}

    assert a.restrict({a: 0}) == 0
    assert a.restrict({a: 1}) == 1
    assert a.restrict({b: 0}) == a

    assert a.compose({a: b}) == b
    assert a.compose({b: c}) == a

    # Expression
    assert str(a) == 'a'
    assert str(X[10]) == 'x[10]'
    assert str(Y[1][2][3]) == 'y[1][2][3]'

    assert a.depth == 0
    assert a.factor() == a
    assert a.is_dnf()
    assert a.is_cnf()
    assert a.invert() == -a

def test_comp():
    # Function
    assert (-a).support == {a}

    assert (-a).restrict({a: 0}) == 1
    assert (-a).restrict({a: 1}) == 0
    assert (-a).restrict({b: 0}) == -a

    assert (-a).compose({a: b}) == -b
    assert (-a).compose({b: c}) == -a

    # Expression
    assert (-a).depth == 0
    assert (-a).factor() == -a
    assert (-a).is_dnf()
    assert (-a).is_cnf()
    assert (-a).invert() == a

def test_var_order():
    assert -a < a < -b < b

    assert a < a + b
    assert b < a + b
    assert -a < a + b
    assert -b < a + b

    assert a + b < a + -b
    assert a + b < -a + b
    assert a + b < -a + -b
    assert a + -b < -a + b
    assert a + -b < -a + -b
    assert -a + b < -a + -b

    assert -a * -b < -a * b
    assert -a * -b < a * -b
    assert -a * -b < a * b
    assert -a * b < a * -b
    assert -a * b < a * b
    assert a * -b < a * b

    assert a * b < a * b * c

    assert X[0] < X[1] < X[10]

def test_or():
    # Function
    assert (-a + b).support == {a, b}

    # Expression
    assert Or() == 0
    assert Or(a) == a

    assert Or(0, 0) == 0
    assert Or(0, 1) == 1
    assert Or(1, 0) == 1
    assert Or(1, 1) == 1

    assert Or(0, 0, 0) == 0
    assert Or(0, 0, 1) == 1
    assert Or(0, 1, 0) == 1
    assert Or(0, 1, 1) == 1
    assert Or(1, 0, 0) == 1
    assert Or(1, 0, 1) == 1
    assert Or(1, 1, 0) == 1
    assert Or(1, 1, 1) == 1

    assert 0 + a == a
    assert a + 0 == a
    assert 1 + a == 1
    assert a + 1 == 1

    assert (0 + a + b).equivalent(a + b)
    assert (a + b + 0).equivalent(a + b)
    assert (1 + a + b) == 1
    assert (a + b + 1) == 1

    # associative
    assert str((a + b) + c + d) == "a + b + c + d"
    assert str(a + (b + c) + d) == "a + b + c + d"
    assert str(a + b + (c + d)) == "a + b + c + d"
    assert str((a + b) + (c + d)) == "a + b + c + d"
    assert str((a + b + c) + d) == "a + b + c + d"
    assert str(a + (b + c + d)) == "a + b + c + d"
    assert str(a + (b + (c + d))) == "a + b + c + d"
    assert str(((a + b) + c) + d) == "a + b + c + d"

    # idempotent
    assert a + a == a
    assert a + a + a == a
    assert a + a + a + a == a
    assert (a + a) + (a + a) == a

    # iverse
    assert -a + a == 1
    assert a + -a == 1

    f = -a * b * c + a * -b * c + a * b * -c
    assert f.restrict({a: 0}).equivalent(b * c)
    assert f.restrict({a: 1}).equivalent(Xor(b, c))
    assert f.restrict({a: 0, b: 0}) == 0
    assert f.restrict({a: 0, b: 1}) == c
    assert f.restrict({a: 1, b: 0}) == c
    assert f.restrict({a: 1, b: 1}) == -c

    assert f_or(a >> b, c >> d).equivalent(-a + b + -c + d)

def test_nor():
    assert Nor(a, b).equivalent(-a * -b)
    assert str(f_nor(a, b)) == "a' * b'"

def test_and():
    # Function
    assert (-a * b).support == {a, b}

    # Expression
    assert And() == 1
    assert And(a) == a

    assert And(0, 0) == 0
    assert And(0, 1) == 0
    assert And(1, 0) == 0
    assert And(1, 1) == 1

    assert And(0, 0, 0) == 0
    assert And(0, 0, 1) == 0
    assert And(0, 1, 0) == 0
    assert And(0, 1, 1) == 0
    assert And(1, 0, 0) == 0
    assert And(1, 0, 1) == 0
    assert And(1, 1, 0) == 0
    assert And(1, 1, 1) == 1

    assert 0 * a == 0
    assert a * 0 == 0
    assert 1 * a == a
    assert a * 1 == a

    assert (0 * a * b) == 0
    assert (a * b * 0) == 0
    assert (1 * a * b).equivalent(a * b)
    assert (a * b * 1).equivalent(a * b)

    # associative
    assert str((a * b) * c * d) == "a * b * c * d"
    assert str(a * (b * c) * d) == "a * b * c * d"
    assert str(a * b * (c * d)) == "a * b * c * d"
    assert str((a * b) * (c * d)) == "a * b * c * d"
    assert str((a * b * c) * d) == "a * b * c * d"
    assert str(a * (b * c * d)) == "a * b * c * d"
    assert str(a * (b * (c * d))) == "a * b * c * d"
    assert str(((a * b) * c) * d) == "a * b * c * d"

    # idempotent
    assert a * a == a
    assert a * a * a == a
    assert a * a * a * a == a
    assert (a * a) + (a * a) == a

    # inverse
    assert -a * a == 0
    assert a * -a == 0

    f = (-a + b + c) * (a + -b + c) * (a + b + -c)
    assert f.restrict({a: 0}).equivalent(Xnor(b, c))
    assert f.restrict({a: 1}).equivalent(b + c)
    assert f.restrict({a: 0, b: 0}) == -c
    assert f.restrict({a: 0, b: 1}) == c
    assert f.restrict({a: 1, b: 0}) == c
    assert f.restrict({a: 1, b: 1}) == 1

    assert f_and(a >> b, c >> d).equivalent((-a + b) * (-c + d))

def test_nand():
    assert Nand(a, b).equivalent(-a + -b)
    assert str(f_nand(a, b)) == "a' + b'"

def test_not():
    # Function
    assert Not(-a + b).support == {a, b}

    # Expression
    assert Not(0) == 1
    assert Not(1) == 0
    assert Not(a) == -a
    assert Not(-a) == a

    assert -(-a) == a
    assert -(-(-a)) == -a
    assert -(-(-(-a))) == a

    assert Not(a + -a) == 0
    assert Not(a * -a) == 1

    assert f_not(-a * b * -c * d).equivalent(a + -b + c + -d)
    assert f_not(-a + b + -c + d).equivalent(a * -b * c * -d)

def test_xor():
    # Function
    assert Xor(-a, b).support == {a, b}

    # Expression
    assert Xor() == 0
    assert Xor(a) == a

    assert Xor(0, 0) == 0
    assert Xor(0, 1) == 1
    assert Xor(1, 0) == 1
    assert Xor(1, 1) == 0

    assert Xor(0, 0, 0) == 0
    assert Xor(0, 0, 1) == 1
    assert Xor(0, 1, 0) == 1
    assert Xor(0, 1, 1) == 0
    assert Xor(1, 0, 0) == 1
    assert Xor(1, 0, 1) == 0
    assert Xor(1, 1, 0) == 0
    assert Xor(1, 1, 1) == 1

    assert Xor(0, a) == a
    assert Xor(a, 0) == a
    assert Xor(1, a) == -a
    assert Xor(a, 1) == -a

    assert Xor(a, a) == 0
    assert Xor(a, -a) == 1
    assert Xor(-a, a) == 1

    assert f_xor(a, b).equivalent(-a * b + a * -b)
    assert f_xor(a, b, c).equivalent(-a * -b * c + -a * b * -c + a * -b * -c + a * b * c)

def test_xnor():
    # Function
    assert Xnor(-a, b).support == {a, b}

    # Expression
    assert Xnor() == 1
    assert Xnor(a) == -a

    assert Xnor(0, 0) == 1
    assert Xnor(0, 1) == 0
    assert Xnor(1, 0) == 0
    assert Xnor(1, 1) == 1

    assert Xnor(0, 0, 0) == 1
    assert Xnor(0, 0, 1) == 0
    assert Xnor(0, 1, 0) == 0
    assert Xnor(0, 1, 1) == 1
    assert Xnor(1, 0, 0) == 0
    assert Xnor(1, 0, 1) == 1
    assert Xnor(1, 1, 0) == 1
    assert Xnor(1, 1, 1) == 0

    assert Xnor(0, a) == -a
    assert Xnor(a, 0) == -a
    assert Xnor(1, a) == a
    assert Xnor(a, 1) == a

    assert Xnor(a, a) == 1
    assert Xnor(a, -a) == 0
    assert Xnor(-a, a) == 0

    assert f_xnor(a, b).equivalent(-a * -b + a * b)
    assert f_xnor(a, b, c).equivalent(-a * -b * -c + -a * b * c + a * -b * c + a * b * -c)

def test_equal():
    # Function
    assert Equal(-a, b).support == {a, b}

    # Expression
    assert Equal() == 1
    assert Equal(a) == 1

    assert Equal(0, 0) == 1
    assert Equal(0, 1) == 0
    assert Equal(1, 0) == 0
    assert Equal(1, 1) == 1

    assert Equal(0, 0, 0) == 1
    assert Equal(0, 0, 1) == 0
    assert Equal(0, 1, 0) == 0
    assert Equal(0, 1, 1) == 0
    assert Equal(1, 0, 0) == 0
    assert Equal(1, 0, 1) == 0
    assert Equal(1, 1, 0) == 0
    assert Equal(1, 1, 1) == 1

    assert Equal(0, a) == -a
    assert Equal(a, 0) == -a
    assert Equal(1, a) == a
    assert Equal(a, 1) == a

    assert Equal(a, a) == 1
    assert Equal(a, -a) == 0
    assert Equal(-a, a) == 0

    assert f_equal(a, b).equivalent(-a * -b + a * b)
    assert f_equal(a, b, c).equivalent(-a * -b * -c + a * b * c)

def test_implies():
    # Function
    assert Implies(-p, q).support == {p, q}

    # Expression
    assert Implies(0, 0) == 1
    assert Implies(0, 1) == 1
    assert Implies(1, 0) == 0
    assert Implies(1, 1) == 1

    assert (0 >> p) == 1
    assert (1 >> p) == p
    assert (p >> 0) == -p
    assert (p >> 1) == 1

    assert (p >> p) == 1
    assert (p >> -p) == -p
    assert (-p >> p) == p

    assert str(p >> q) == "p => q"
    assert str((a * b) >> (c + d)) == "(a * b) => (c + d)"

    assert (p >> q).restrict({p: 0}) == 1
    assert (p >> q).compose({q: a}).equivalent(p >> a)
    assert (p >> q).invert().equivalent(p * -q)
    assert ((a * b) >> (c + d)).depth == 2

    f = Implies(p, 1, simplify=False)
    assert str(f) == "p => 1"
    assert simplify(f) == 1

    assert f_implies(p, q).equivalent(-p + q)

def test_ite():
    # Function
    assert ITE(s, -a, b).support == {s, a, b}

    # Expression
    assert ITE(0, 0, 0) == 0
    assert ITE(0, 0, 1) == 1
    assert ITE(0, 1, 0) == 0
    assert ITE(0, 1, 1) == 1
    assert ITE(1, 0, 0) == 0
    assert ITE(1, 0, 1) == 0
    assert ITE(1, 1, 0) == 1
    assert ITE(1, 1, 1) == 1

    assert ITE(0, 0, b) == b
    assert ITE(0, a, 0) == 0
    assert ITE(0, 1, b) == b
    assert ITE(0, a, 1) == 1
    assert ITE(1, 0, b) == 0
    assert ITE(1, a, 0) == a
    assert ITE(1, 1, b) == 1
    assert ITE(1, a, 1) == a

    assert ITE(s, 0, 0) == 0
    assert ITE(s, 0, 1) == -s
    assert ITE(s, 1, 0) == s
    assert ITE(s, 1, 1) == 1
    assert ITE(s, 0, b).equivalent(-s * b)
    assert ITE(s, a, 0).equivalent(s * a)
    assert ITE(s, 1, b).equivalent(s + b)
    assert ITE(s, a, 1).equivalent(-s + a)

    assert ITE(s, -a, -a) == -a
    assert ITE(s, a, a) == a

    assert str(ITE(s, a, b)) == "s ? a : b"
    assert str(ITE(s, a * b, c + d)) == "s ? (a * b) : (c + d)"

    assert ITE(s, a, b).restrict({a: 1, b: 1}) == 1
    assert ITE(s, a, b).compose({a: b, b: a}).equivalent(s * b + -s * a)
    assert ITE(s, a, b).invert().equivalent((-s + -a) * (s + -b))
    assert ITE(s, a * b, c + d).depth == 3

    f = ITE(s, 1, 1, simplify=False)
    assert str(f) == "s ? 1 : 1"
    assert simplify(f) == 1

    assert f_ite(s, a, b).equivalent(s * a + -s * b)

def test_absorb():
    assert (a * b + a * b).absorb().equivalent(a * b)
    assert (a * (a + b)).absorb() == a
    assert ((a + b) * a).absorb() == a
    assert (-a * (-a + b)).absorb() == -a
    assert (a * b * (a + c)).absorb().equivalent(a * b)
    assert (a * b * (a + c) * (a + d)).absorb().equivalent(a * b)
    assert (-a * b * (-a + c)).absorb().equivalent(-a * b)
    assert (-a * b * (-a + c) * (-a + d)).absorb().equivalent(-a * b)
    assert (a * -b + a * -b * c).absorb().equivalent(a * -b)
    assert ((a + -b) * (a + -b + c)).absorb().equivalent(a + -b)
    assert ((a + -b + c) * (a + -b)).absorb().equivalent(a + -b)

def test_reduce():
    f = a * b + a * c + b * c
    assert str(f.reduce()) == "a' * b * c + a * b' * c + a * b * c' + a * b * c"
    assert str(f.reduce(conj=True)) == "(a + b + c) * (a + b + c') * (a + b' + c) * (a' + b + c)"

def test_expand():
    assert a.expand() == a

    f = a.expand(b)
    assert len(f.args) == 2 and f.equivalent(a)

    f = a.expand([b, c])
    assert len(f.args) == 4 and f.equivalent(a)

    assert a.expand(conj=True) == a

    f = a.expand(b, conj=True)
    assert len(f.args) == 2 and f.equivalent(a)

    f = a.expand([b, c], conj=True)
    assert len(f.args) == 4 and f.equivalent(a)

def test_satisfy():
    f = a * -b * c * -d
    assert f.satisfy_one(algorithm='backtrack') == {a: 1, b: 0, c: 1, d: 0}
    assert f.satisfy_one(algorithm='dpll') == {a: 1, b: 0, c: 1, d: 0}

    f = a * b + a * c + b * c
    nose.tools.assert_raises(TypeError, f.satisfy_one, 'dpll')

    points = [p for p in Xor(a, b, c).satisfy_all()]
    assert points == [
        {a: 1, b: 0, c: 0},
        {a: 0, b: 1, c: 0},
        {a: 0, b: 0, c: 1},
        {a: 1, b: 1, c: 1},
    ]
    assert Xor(a, b, c).satisfy_count() == 4

def test_depth():
    assert (a + b).depth == 1
    assert (a + (b * c)).depth == 2
    assert (a + (b * (c + d))).depth == 3

    assert (a * b).depth == 1
    assert (a * (b + c)).depth == 2
    assert (a * (b + (c * d))).depth == 3

    assert Not(a + b).depth == 1
    assert Not(a + (b * c)).depth == 2
    assert Not(a + (b * (c + d))).depth == 3

    assert Xor(a, b, c).depth == 2
    assert Xor(a, b, c + d).depth == 3
    assert Xor(a, b, c + Xor(d, e)).depth == 5

    assert Equal(a, b, c).depth == 2
    assert Equal(a, b, c + d).depth == 3
    assert Equal(a, b, c + Xor(d, e)).depth == 5

    assert Implies(p, q).depth == 1
    assert Implies(p, a + b).depth == 2
    assert Implies(p, Xor(a, b)).depth == 3

    assert ITE(s, a, b).depth == 2
    assert ITE(s, a + b, b).depth == 3
    assert ITE(s, a + b, Xor(a, b)).depth == 4

def test_terms():
    f = a * b + a * c + b * c
    assert str(sorted(f.minterms)) == "[a' * b * c, a * b' * c, a * b * c', a * b * c]"
    assert str(sorted(f.maxterms)) == "[a + b + c, a + b + c', a + b' + c, a' + b + c]"

def test_indices():
    f = a * b + a * c + b * c
    assert f.min_indices == {3, 5, 6, 7}
    assert f.max_indices == {0, 1, 2, 4}

def test_nf():
    f = Xor(a, b, c)
    g = a * b + a * c + b * c

    assert str(f.to_dnf()) == "a' * b' * c + a' * b * c' + a * b' * c' + a * b * c"
    assert str(f.to_cnf()) == "(a + b + c) * (a + b' + c') * (a' + b + c') * (a' + b' + c)"

    assert str(g.to_cdnf()) == "a' * b * c + a * b' * c + a * b * c' + a * b * c"
    assert str(g.to_ccnf()) == "(a + b + c) * (a + b + c') * (a + b' + c) * (a' + b + c)"

    assert g.min_indices == {3, 5, 6, 7}
    assert g.max_indices == {0, 1, 2, 4}

def test_is_nf():
    assert (a + b + c).is_dnf()
    assert (a + (b * c) + (c * d)).is_dnf()
    assert not ((a * b) + (b * (c + d))).is_dnf()

    assert (a * b * c).is_cnf()
    assert (a * (b + c) * (c + d)).is_cnf()
    assert not ((a + b) * (b + c * d)).is_cnf()

    assert not Equal(a, b, c).is_dnf()
    assert not Implies(p, q).is_dnf()
    assert not ITE(s, a, b).is_dnf()
    assert not Equal(a, b, c).is_cnf()
    assert not Implies(p, q).is_cnf()
    assert not ITE(s, a, b).is_cnf()

def test_misc():
    f = a * b + a * c + b * c

    assert f.smoothing(a).equivalent(b + c)
    assert f.consensus(a).equivalent(b * c)
    assert f.derivative(a).equivalent(Xor(b, c))
