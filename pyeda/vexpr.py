"""
Boolean Vector Logic Expressions

Interface Functions:
    bitvec
    uint2vec
    int2vec

Interface Classes:
    BitVector
"""

from pyeda.common import clog2, bit_on
from pyeda.boolfunc import Slicer, VectorFunction
from pyeda.expr import var, Not, Or, And, Xor, Xnor

def bitvec(name, *slices):
    """Return a vector of variables."""
    sls = list()
    for sl in slices:
        if type(sl) is int:
            sls.append(slice(0, sl))
        elif type(sl) is tuple and len(sl) == 2:
            if sl[0] < sl[1]:
                sls.append(slice(sl[0], sl[1]))
            else:
                sls.append(slice(sl[1], sl[0]))
        else:
            raise ValueError("invalid argument")
    return _rbitvec(name, sls, tuple())

def _rbitvec(name, slices, indices):
    fst, rst = slices[0], slices[1:]
    if rst:
        items = [ _rbitvec(name, rst, indices + (i, ))
                  for i in range(fst.start, fst.stop) ]
        return Slicer(items, fst.start)
    else:
        vs = [var(name, indices + (i, )) for i in range(fst.start, fst.stop)]
        return BitVector(vs, fst.start)

def uint2vec(num, length=None):
    """Convert an unsigned integer to a BitVector."""
    assert num >= 0

    items = list()
    while num != 0:
        items.append(num & 1)
        num >>= 1

    if length:
        if length < len(items):
            raise ValueError("overflow: " + str(num))
        else:
            while len(items) < length:
                items.append(0)

    return BitVector(items)

def int2vec(num, length=None):
    """Convert a signed integer to a BitVector."""
    if num < 0:
        req_length = clog2(abs(num)) + 1
        bv = uint2vec(2 ** req_length + num)
    else:
        req_length = clog2(num + 1) + 1
        bv = uint2vec(num, req_length)

    if length:
        if length < req_length:
            raise ValueError("overflow: " + str(num))
        else:
            bv.sext(length - req_length)

    return bv


class BitVector(VectorFunction):
    """Vector Expression with logical functions."""

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.items)

    # Operators
    def uor(self):
        return Or(*self)

    def uand(self):
        return And(*self)

    def uxor(self):
        return Xor(*self)

    def __invert__(self):
        items = [Not(f) for f in self]
        return self.__class__(items, self.start)

    def __or__(self, other):
        items = [Or(*t) for t in zip(self, other)]
        return self.__class__(items)

    def __and__(self, other):
        items = [And(*t) for t in zip(self, other)]
        return self.__class__(items)

    def __xor__(self, other):
        items = [Xor(*t) for t in zip(self, other)]
        return self.__class__(items)

    # Shift operators
    def lsh(self, y, cin=None):
        assert 0 <= y <= len(self)
        if cin is None:
            cin = BitVector([0] * y)
        else:
            assert len(cin) == y
        if y == 0:
            return self, BitVector([])
        else:
            return ( BitVector(cin.items + self.items[:-y], self.start),
                     BitVector(self.items[-y:]) )

    def rsh(self, y, cin=None):
        assert 0 <= y <= len(self)
        if cin is None:
            cin = BitVector([0] * y)
        else:
            assert len(cin) == y
        if y == 0:
            return self, BitVector([])
        else:
            return ( BitVector(self.items[y:] + cin.items, self.start),
                     BitVector(self.items[:y]) )

    def arsh(self, y):
        assert 0 <= y <= len(self)
        if y == 0:
            return self, BitVector([])
        else:
            sign = self.items[-1]
            return ( BitVector(self.items[y:] + [sign] * y, self.start),
                     BitVector(self.items[:y]) )

    # Other logic
    def decode(self):
        """Return symbolic logic for an N-2^N binary decoder.

        Example Truth Table for a 2:4 decoder:

            +===========+=====================+
            | A[1] A[0] | D[3] D[2] D[1] D[0] |
            +===========+=====================+
            |   0    0  |   0    0    0    1  |
            |   0    1  |   0    0    1    0  |
            |   1    0  |   0    1    0    0  |
            |   1    1  |   1    0    0    0  |
            +===========+=====================+

        >>> A = bitvec('a', 2)
        >>> d = A.decode()
        >>> d.vrestrict({A: "00"})
        [1, 0, 0, 0]
        >>> d.vrestrict({A: "10"})
        [0, 1, 0, 0]
        >>> d.vrestrict({A: "01"})
        [0, 0, 1, 0]
        >>> d.vrestrict({A: "11"})
        [0, 0, 0, 1]
        """
        items = [ And(*[ f if bit_on(i, j) else -f
                         for j, f in enumerate(self) ])
                  for i in range(2 ** len(self)) ]
        return self.__class__(items)
