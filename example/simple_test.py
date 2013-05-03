from pyeda import *
import pprint as pp

import  graph_tool.all  as gt


# Test a few features of pyeda to check how to use some functions

def bdd2dict(bdd):
     """
     Transform a BDD created by pyeda.bdd function to a dictionnary
     """
     if type(bdd.root) is int:
         return {bdd.root:bdd.root}
     if type(bdd.root) is pyeda.boolfunc.Variable:
         var_name = str(bdd.root)
         return {"var" : var_name,'zero' : bdd2dict(bdd.low),'one' : bdd2dict(bdd.high)}
     print("Unrecognized type for bdd.root : %s" % (type(bdd.root)))



def simple_bdd(bf,ordering=None):
     """
     A simple BDD building algorithm, return a tree build from dictionnaries
     
     Arguments:
     - `bf`: A boolean function
     """
     if ordering is None:
          support = list(bf.support)
     else:
          support = ordering
     

     top = support[0]

     print("Top = %s" % (top))
     cf_false,cf_true = bf.cofactors(top)
     print (cf_true,cf_false)
     
     if type(cf_true) is int:
          true_val = cf_true
     else:
          true_val = simple_bdd(cf_true,support[1:])
     if type(cf_false) is int:
          false_val = cf_false
     else:
          false_val = simple_bdd(cf_false,support[1:])
     return {
          "var" : str(top),
          "true" : true_val,
          "false" : false_val
          }

# This need serious clean-up to get the vertices label correct and get rid of all the string concatenation thing
def bdd2dot(bdd):
     """Transform a BDD to a dot representation to generate images using the graphviz toolbox
     
     Arguments:
     - `bdd`: a dictionnary representing the BDD
     """
     dot_str = "digraph G {\n"
     statements = list()
     _bdd2dot(None,bdd,statements)
     return dot_str + "\n".join(statements) + "\n}\n"
     
def _bdd2dot(var,bdd,statements,branch=False,index=0,rank=0):
     """ internal function, recursive
     Arguments:
     - `var`: The current "root" variable
     - 'bdd': one of the (sub-)bdd rooted at var
     - statements : list of dot statement that will be updated accross calls
     - branch : whether we are on the 0/False or 1/True branch

     """

     if type(bdd) is int:
          if var is not None:
               statements.append("{rank=sink; _" + str(bdd) + "_" + str(index) + " ; }")
               if branch:
                    statements.append(var + " -> _" + str(bdd) + "_" + str(index) + " [label=\"1\"];")
               else:
                    statements.append(var + " -> _" + str(bdd) + "_" + str(index) + " [style=dotted,label=\"0\"] ;")
          else:
               statements.append(str(bdd) + " ;")
          return 1
     else:
          v_f = bdd['false']
          v_t = bdd['true']
          v_v = bdd['var'] 
          if var is not None:
               if branch:
                    statements.append(var + " -> " + v_v + "_" + str(index) + " [label=\"1\"];")
               else:
                    statements.append(var + " -> " + v_v + "_" + str(index) + " [style=dotted,label=\"0\"];")                         
          idx1 = _bdd2dot(v_v  + "_" + str(index),v_t,statements,True,index)
          idx2 = _bdd2dot(v_v  + "_" + str(index),v_f,statements,False,index+idx1)
          return idx1+idx2
               
               
# graph_tool interface
# same as above - some clean-up is needed
class gtBDD(object):
      def __init__(self):
        """Create a new graph_tool Graph object (directed graph)
        """
        self.g = gt.Graph()

        self.vprops = dict()
        self.eprops = dict()
        self.gprops = dict()

        self.vprops['label']  = self.g.new_vertex_property("string") # 'label' is a 'dot' property
        self.vprops['rank']  = self.g.new_vertex_property("string")  # 'rank' is a 'dot' property
        self.eprops['label']  = self.g.new_edge_property("string") # 'label' is a 'dot' property
        self.gprops['__________'] = None # should not be empty
        self.v_lut = dict() # key = name, value = vertex 

      def add_vertex(self,v_name,rank=None):
        """Add a vertex to the graph and store its name
           If a vertex with same name already exists, we skip the  creation
        """
        if v_name not in self.v_lut:
             v = self.g.add_vertex()
             self.vprops['label'][v] = v_name
             self.v_lut[v_name] = v
             if rank is not None:
                  self.vprops['rank'][v] = rank

      def add_edge(self,v1,v2,e_name):
        """Add an edge to the graph between vertices named v1 and v2 and store its name
        """
        e = self.g.add_edge(
             self.v_lut[v1],
             self.v_lut[v2],
             )
        self.eprops['label'][e] = e_name

      def draw_svg(self,filename="graph.svg"):
        gt.graphviz_draw(self.g, 
                     # pos=pos,
                     vprops=self.vprops,
                     eprops=self.eprops,
                     gprops=self.gprops,
                     layout='dot',
                     output=filename)



           



def bdd2gt(bdd):
     """Build a graph_tool from a bdd
     
     Arguments:
     - `bdd`: a dictionnary representing the bdd
     """
     g = gtBDD()
     _bdd2gt(graph=g,var=None,bdd=bdd)
     return g


def _bdd2gt(graph,var,bdd,branch=False,index=0,rank=0):
     if type(bdd) is int: # leaf node, but must not be duplicated
          bdd_str = str(bdd) + "_" + str(index)
          graph.add_vertex(bdd_str,rank='sink')
          e_label = "1"  if branch else "0" 
          if var is not None:
               # there is a "parent"
               graph.add_edge(var,bdd_str,e_label)
          
          return 1 
     else:
          v_f = bdd['false']
          v_t = bdd['true']
          v_v = bdd['var'] 
          print("v_v = %s" %(v_v))
          v_name = v_v + str(index)
          graph.add_vertex(v_name)
          if var is not None:
               if branch:
                    graph.add_edge(var,v_name,"1")
               else:
                    graph.add_edge(var,v_name,"0")
         
          nb_idx1 = _bdd2gt(graph=graph,var=v_name,bdd=v_t,branch=True,index=index,rank=rank+1)
          nb_idx2 = _bdd2gt(graph=graph,var=v_name,bdd=v_f,branch=False,index=index+nb_idx1,rank=rank+1)
          return nb_idx1 + nb_idx2





def init_T(bdd):
     """Initialize the T table
     """ 
     bdd['T'][0] = (bdd["n"]+1,None,None) # (Leaves are using max index+1) 
     bdd['T'][1] = (bdd["n"]+1,None,None) # (Leaves are using max index+1) 
     # "u" is already set to 1...
     
def add_T(bdd,i,l,h):
     """ Add a new entry in the T table
     return a new node number
     """
     u = bdd["u"] + 1
     bdd["T"][u] = (i,l,h)
     bdd["u"] = u
     return u

def member_H(bdd,i,l,h):
     return (i,l,h) in bdd["H"]

def lookup_H(bdd,i,l,h):
     return  bdd["H"][(i,l,h)]

def insert_H(bdd,i,l,h,u):
     bdd["H"][(i,l,h)] = u

def MK(bdd,i,l,h):
     """MK (make) function
     Arguments:
     - `bdd`: the current bdd under construction
     - `i`: : the variable index (x_i) (i=1 : top)
     - `l`: : node number for 'low' branch
     - `h`: : node number for 'high' branch
     """
     if l == h : return l
     if member_H(bdd,i,l,h):
          return lookup_H(bdd,i,l,h)
     else:
          u = add_T(bdd,i,l,h)
          insert_H(bdd,i,l,h,u)
          return u
     
def _build(bdd,expr,i):
     """
     
     Arguments:
     - `bdd` : bdd under construction
     - `expr`: the boolean expression for variable i
     - `i`   : variable index (i = 1 : top)
     """

     
     
     print("_build " + '-'*20)
     print("_build : expr = %s" % (expr))
     print("_build : i    = %d" % (i))
     print("_build : bdd  = %s" % (bdd))
     print("_build : n  = %s" % (bdd["n"]))
    
     

     
     if i> bdd["n"]: # we have reach the leaves
          print "End reached !"
          if expr:
               return 1
          else:
               return 0
     else:
          print "Continuing !"
          var = bdd["support"][i-1]
          print("_build : var  = %s" % (var))
          if type(expr) is int:
               cf_false = expr
               cf_true  = expr
          else:
               cf_false,cf_true = expr.cofactors(var)
               print("_build : cofactors for var = %s" %(var))
               print("_build : cfalse = %s" %(cf_false))
               print("_build : ctrue = %s" %(cf_true))
          v0 = _build(bdd,cf_false ,i+1)
          v1 = _build(bdd,cf_true,i+1)
          return MK(bdd,i,v0,v1)
          
          
          
     
def simple_robdd(bf,ordering=None):
     """
     A simple ROBDD building algorithm
     
     Arguments:
     - `bf`: A boolean function
     - `ordering` : A list of boolean variables, to define order (first at top)
     """

          
     

     if ordering is None:
          support = list(bf.support)
     else:
          support = ordering

     bdd = {
          "u" : 1, # Node number (0 and 1 are reseverd for the two terminal nodes)
          "n" : len(bf.support), # variable will be indexed for 1 to n (with variable i)
          "support" : support,
          'H' : dict(),
          'T' : dict(),  # Index : node number , value (i,h,l) : i : variable index
                         # h : node number, 'high'/1  , l : node_number 'low'/0
          
          }

     init_T(bdd)
     _build(bdd,bf,1)
     return bdd


          
     
    


if __name__ == '__main__':
    # create 3 boolean variables x,y,z
    x,y,z = map(var,'xyz')
    

    # f and g : Boolean functions to be checked for equivalence
    f = x*y*z # -x = !x
    g = x+ (-y) 

    
#    print("type x=%s" %(type(x)))
#    
#    cofactors_f = f.cofactors(x)
#    print cofactors_f
#
#    bdd_f = expr2bdd(f)
#    pp.pprint(bdd_f)
#
#    bdd_f_dic = bdd2dict(bdd_f)
#    
#    pp.pprint(bdd_f_dic)
#
#    print '*'*80
#    bdd_f_dic2 = simple_bdd(f)
#    
#    pp.pprint(bdd_f_dic2)
#
#    print '='*80    
#    print(bdd2dot(bdd_f_dic2))
#
#    # graph_tool testing
#    graph = bdd2gt(bdd_f_dic2)
#    graph.draw(filename="bdd_f_dic2.svg")
    

    a,b,c = map(var,'abc')

    h = c* ( a + b) 
    bdd_h = simple_bdd(h,[a,b,c])
    pp.pprint(bdd_h)

    #graph = bdd2gt(bdd_h)
    #graph.draw_svg(filename="bdd_h.svg")

    print(bdd2dot(bdd_h))
    with open("bdd_h.dot","w") as f:
         f.write(bdd2dot(bdd_h))
         f.close()


    robdd_h = simple_robdd(h,[a,b,c])
    pp.pprint(robdd_h)
