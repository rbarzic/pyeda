from pyeda import *
import pprint as pp

import graph_tool.all  as gt




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

def attributes2dot(label=None,style=None):
    attribute = list()
    if style is not None:
        attribute.append( "style=" + style)
    if label is not None:
        attribute.append("label=\"" + label + "\"")
    if attribute:
        return " [" + ','.join(attribute) + "] "
    else:
        return ""


def edge2dot(v1,v2,label=None,style=None):
    """Return a dot string that represents an edge between v1 and v2
    
    Arguments:
    - `v1`:
    - `v2`:
    - `label`:
    - `style`:
    """
    attributes = attributes2dot(label=label,style=style)
    return "_" + str(v1) + " -> _" + str(v2) + attributes + ";"


def vertex2dot(v,label=None,style=None,rank=None):
    """Return a dot string that represents an vertex
    
    Arguments:
    - `v`: internale vertex name (an underscore will be added in front in case it is a number)
    - `label`: The label that will be display
    - `style`: Dot style to apply
    - `rank` : Dot rank (source/sink/min/max...)
    """
    attributes = attributes2dot(label=label,style=style)
    main_str =  "_" + str(v) + attributes
    if rank is None:
        return main_str + ";"
    else:
        return "{rank=" + rank + ";  "+ main_str + "; }"
 

    


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


# ROBDD code


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

    if i> bdd["n"]: # we have reach the leaves
         if expr:
              return 1
         else:
              return 0
    else:
         var = bdd["support"][i-1]
         if type(expr) is int:
              cf_false = expr
              cf_true  = expr
         else:
              cf_false,cf_true = expr.cofactors(var)
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





     
def Apply(op,bdd1,bdd2):
    """Apply an boolean operator between the two boolean functions
 represented by their robdd u1 and u2 and return a new robdd
     
     Arguments:
     - `op`: boolean operator (and,or...)
     - `bdd1`: 1st ROBDD
     - `bdd2`: 2nd ROBDD
     """
     # First, the support for the two robdds may not be the same...
     # This is a "problem" has each robdd is in fact represented as a table using indexes

    sup1 = bdd1["support"]
    sup2 = bdd2["support"]

    t1 = bdd1['H']
    t2 = bdd2['H']
    
    G = dict()

    new_support = list(set(sup1 + sup2)) # we use list because we want to use index()
    l_new_support = len(new_support)


    def get_u(t):
         """return the top node in the T table t
         """
         return len(t) 


    def var_idx(u,t,sup):
         """Return the "new" index (inside the new support) for entry  u in table t (of type T)          
            We need the old support to do the look-up
         """
         # first get the "old" variable index
         old_idx,_,_ = t[u] 
         
         return new_support.index( sup[old_idx] )
    def low_t(u,t):
         _,low,_ = t[u]
         return low

    def high_t(u,t):
         _,_,high = t[u]
         return high

    def App(bdd,u1,u2):
         """ The recursive function, doing all the work. It operates on a "T" hash table (inside bdd)  (u->(i,l,h)
         """
         u = 99999 # just to detect if something is wrong
         if (u1,u2) in G:
              return G[(u1,u2)]
         elif (u1 in (0,1)) and (u2 in (0,1)):               
              u = op(u1,u2)
         elif var_idx(u1,t1,sup1) ==  var_idx(u2,t2,sup2):
              u = MK(bdd=bdd,
                     i= var_idx(u1,t1,sup1),
                     l= App(low_t(u1,t1),low(u2,t2)),
                     h= App(high_t(u1,t1),high_t(u2,t2))
                     )

         elif var_idx(u1,t1,sup1) <  var_idx(u2,t2,sup2):
              u = MK(bdd=bdd,
                     i= var_idx(u1,t1,sup1),
                     l= App(),
                     h= App())

              pass
         else: # var_idx(u1) >  var_idx(u2):
              u = MK(bdd=bdd,
                     i= var_idx(u2,t2,sup2),
                     l= App(),
                     h= App())

              pass
         
         G[(u1,u2)] = u
         return u

    # result bdd
    bdd = {
         "u" : 1, # Node number (0 and 1 are reserved for the two terminal nodes)
         "n" : l_new_support, # variable will be indexed for 1 to n (with variable i)
         "support" : new_support,
         'H' : dict(),
         'T' : dict(),  # Index : node number , value (i,h,l) : i : variable index
         # h : node number, 'high'/1  , l : node_number 'low'/0
         
         }

    init_T(bdd)

    pp.pprint(new_support)
    App(bdd,get_u(t1),get_u(t2))


def robdd2dot(robdd):
    """Return a dot representation of robdd

    Arguments:
    - `robdd`: A reduced, oriented, binary decision diagram
    """
    dot_str = "digraph G {\n"
    statements = list()
    t_table = robdd['T']
    n = robdd['n']
    support = robdd['support']
    pp.pprint(t_table)
    vertex_already_generated = dict()
    # for u,(var_idx,low,high) in  t_table:
    for u,val in  t_table.items():
        (var_idx,low,high) = val
        if var_idx == n+1: # Nodes 0 or 1
            statements.append(vertex2dot(v=u,label=str(u),rank="sink"))
        else: # "normal nodes" (boolean variables)
            if var_idx not in vertex_already_generated:
                var = support[var_idx-1]
                statements.append(vertex2dot(v=u,label=str(var)))
                vertex_already_generated[var_idx] = 'yes'
            statements.append(edge2dot(u,low,style="dotted",label="0"))
            statements.append(edge2dot(u,high,label="1"))

    return dot_str +  "\n".join(statements) + "\n}\n"




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

    g = b + (-c)
    robdd_g = simple_robdd(g,[b,c])
    pp.pprint(robdd_g)

    Apply("and",robdd_h,robdd_g)

#    robdd2dot(robdd_h)
#    print(robdd2dot(robdd_h))
#    with open("robdd_h.dot","w") as f:
#        f.write(robdd2dot(robdd_h))
#        f.close()

