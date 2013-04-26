from pyeda import *
import pprint as pp

# Test a few features of pyeda to check how to use some functions

def bdd2dict(bdd):
     """
     Transform a BDD greated by pyeda.bdd funtion to a dictionnary
     """
     if type(bdd.root) is int:
         return {bdd.root:bdd.root}
     if type(bdd.root) is pyeda.boolfunc.Variable:
         var_name = str(bdd.root)
         return {"var" : var_name,'zero' : bdd2dict(bdd.low),'one' : bdd2dict(bdd.high)}
     print("Unrecognized type for bdd.root : %s" % (type(bdd.root)))



def simple_bdd(bf):
     """
     A simple BDD building algorithm, return a tree build from dictionnaries
     
     Arguments:
     - `bf`: A boolean function
     """
     top = list(bf.support)[0]
     print top
     cf_false,cf_true = bf.cofactors(top)
     print (cf_true,cf_false)
     if type(cf_true) is int:
          true_val = cf_true
     else:
          true_val = simple_bdd(cf_true)
     if type(cf_false) is int:
          false_val = cf_false
     else:
          false_val = simple_bdd(cf_false)
     return {
          "var" : str(top),
          "true" : true_val,
          "false" : false_val
          }



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

    print '*'*80
    bdd_f_dic2 = simple_bdd(f)
    
    pp.pprint(bdd_f_dic2)
