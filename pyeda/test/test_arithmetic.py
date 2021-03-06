"""
Test logic functions for digital arithmetic
"""

import random

from pyeda import bitvec, uint2vec, int2vec
from pyeda.arithmetic import ripple_carry_add as rca
from pyeda.arithmetic import kogge_stone_add as ksa
from pyeda.arithmetic import bin2gray, gray2bin

NVECS = 100

def uadd(S, A, B, aval, bval):
    N = len(A)
    R = S.vrestrict({A: uint2vec(aval, N), B: uint2vec(bval, N)})
    return R.to_uint()

def sadd(S, A, B, aval, bval):
    N = len(A)
    R = S.vrestrict({A: int2vec(aval, N), B: int2vec(bval, N)})
    return R.to_int()

def test_unsigned_add():
    A = bitvec('A', 8)
    B = bitvec('B', 8)

    for adder in (rca, ksa):
        S, C = adder(A, B)
        S.append(C[7])

        # 0 + 0 = 0
        assert uadd(S, A, B, 0, 0) == 0
        # 255 + 255 = 510
        assert uadd(S, A, B, 255, 255) == 510
        # 255 + 1 = 256
        assert uadd(S, A, B, 255, 1) == 256

        # unsigned random vectors
        for i in range(NVECS):
            ra = random.randint(0, 2**8-1)
            rb = random.randint(0, 2**8-1)
            assert uadd(S, A, B, ra, rb) == ra + rb

def test_signed_add():
    A = bitvec('A', 8)
    B = bitvec('B', 8)

    for adder in (rca, ksa):
        S, C = adder(A, B)

        # 0 + 0 = 0
        assert sadd(S, A, B, 0, 0) == 0
        # -64 + -64 = -128
        assert sadd(S, A, B, -64, -64) == -128
        # -1 + 1 = 0
        assert sadd(S, A, B, -1, 1) == 0
        # -64 + 64 = 0
        assert sadd(S, A, B, -64, 64) == 0

        # signed random vectors
        for i in range(NVECS):
            ra = random.randint(-2**6, 2**6-1) # -64..63
            rb = random.randint(-2**6, 2**6)   # -64..64
            assert sadd(S, A, B, ra, rb) == ra + rb

        # 64 + 64, overflow
        R = C.vrestrict({A: int2vec(64, 8), B: int2vec(64, 8)})
        assert R[7] != R[6]
        # -65 + -64, overflow
        R = C.vrestrict({A: int2vec(-65, 8), B: int2vec(-64, 8)})
        assert R[7] != R[6]

def test_bin2gray():
    B = bitvec('B', 4)
    G = bin2gray(B)
    gnums = [G.vrestrict({B: uint2vec(i, 4)}).to_uint() for i in range(16)]
    assert gnums == [0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8]

def test_gray2bin():
    G = bitvec('G', 4)
    B = gray2bin(G)
    gnums = [0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8]
    bnums = [B.vrestrict({G: uint2vec(i, 4)}).to_uint() for i in gnums]
    assert bnums == list(range(16))
