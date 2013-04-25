from pyeda import *
import pprint as pp

# Test a few features of pyeda to check how to use some functions

def bdd2dict(bdd):
     if type(bdd.root) is int:
         return {bdd.root:bdd.root}
     if type(bdd.root) is pyeda.boolfunc.Variable:
         var_name = str(bdd.root)
         return {"var" : var_name,'zero' : bdd2dict(bdd.low),'one' : bdd2dict(bdd.high)}
     print("Unrecognized type for bdd.root : %s" % (type(bdd.root)))
     pass


if __name__ == '__main__':
    # create 3 boolean variables x,y,z
    x,y,z = map(var,'xyz')

    # f and g : Boolean functions to be checked for equivalence
    f = x*y*z # -x = !x
    g = x+ (-y) 
    
    print("type x=%s" %(type(x)))
    
    cofactors_f = f.cofactors(x)
    print cofactors_f

    bdd_f = expr2bdd(f)
    pp.pprint(bdd_f)

    bdd_f_dic = bdd2dict(bdd_f)
    
    pp.pprint(bdd_f_dic)

   
