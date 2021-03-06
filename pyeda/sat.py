"""
Boolean Satisfiability

Interface functions:
    backtrack
    dpll
"""

#import random

def backtrack(expr):
    """
    If this function is satisfiable, return a satisfying input point. A
    tautology *may* return an empty dictionary; a contradiction *must*
    return None.

    >>> from pyeda import var
    >>> a, b, c = map(var, "abc")
    >>> point = (-a * b).satisfy_one(algorithm='backtrack')
    >>> sorted(point.items())
    [(a, 0), (b, 1)]
    >>> (-a * -b + -a * b + a * -b + a * b).satisfy_one(algorithm='backtrack')
    {}
    >>> (a * b * (-a + -b)).satisfy_one(algorithm='backtrack')
    """
    v = expr.top
    cfs = {p[v]: cf for p, cf in expr.iter_cofactors(v)}
    if cfs[0] == 1:
        if cfs[1] == 1:
            # tautology
            point = {}
        else:
            # v=0 satisfies the formula
            point = {v: 0}
    elif cfs[1] == 1:
        # v=1 satisfies the formula
        point = {v: 1}
    else:
        for num, cf in cfs.items():
            if cf != 0:
                point = backtrack(cf)
                if point is not None:
                    point[v] = num
                    break
        else:
            point = None
    return point

def dpll(cnf):
    """
    Davis-Putnam-Logemann-Loveland (DPLL) Algorithm
    """
    # 1. Boolean constraint propagation
    cnf, constraints = cnf.bcp()

    if cnf == 0:
        return None
    elif cnf == 1:
        return constraints

    # 2. Pure literal elimination
    cnf, _constraints = cnf.ple()
    constraints.update(_constraints)

    if cnf == 0:
        return None
    elif cnf == 1:
        return constraints

    # 3. Variable selection heuristic
    v = cnf.top
    #v = random.choice(cnf.inputs)

    # 4. Backtracking
    cfs = {p[v]: cf for p, cf in cnf.iter_cofactors(v)}
    if cfs[0] == 1:
        if cfs[1] == 1:
            # tautology
            point = {}
        else:
            # v=0 satisfies the formula
            point = {v: 0}
    elif cfs[1] == 1:
        # v=1 satisfies the formula
        point = {v: 1}
    else:
        for num, cf in cfs.items():
            if cf != 0:
                point = dpll(cf)
                if point is not None:
                    point[v] = num
                    break
        else:
            point = None

    if point is not None:
        point.update(constraints)

    return point
