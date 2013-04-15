from pyeda import *

def print_result(f,g,point):
    if point is not None:
        print("\tFunctions f and g are not identical")
        print("\tCounter example : %s" % (point))
        print("\t    f = %s" %(f.restrict(point)))
        print("\t    g = %s" %(g.restrict(point)))
    else:
        print("\tYes they are !")


if __name__ == '__main__':
    # create 3 boolean variables x,y,z
    x,y,z = map(var,'xyz')

    # f and g : Boolean functions to be checked for equivalence
    f = x*y # -x = !x
    g = x+ (-y) 
    
    
    h = Xor(g,f) 
    
   
    print("""  Checking if 
         function f : %s
       and
         function g : %s

       are equivalent, using SAT-based algorithms
    """ % (f,g))
    print("\nUsing backtrack algorithm....")
    
    point = h.satisfy_one(algorithm='backtrack')
    print_result(f,g,point)


    print("\nUsing DPLL algorithm....")
    # dpll algorithm need cnf format (Conjunctive normal form)
    h = h.to_cnf()
    point  = h.satisfy_one(algorithm='dpll')
    print_result(f,g,point)

