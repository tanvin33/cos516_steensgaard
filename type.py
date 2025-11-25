'''
Code for management of Types as described in Steensgaard's analysis.

As defined by Steensgaard:
- Alpha Types represent values
- Tau Types represent locations or pointers to locations
- Lambda Types represent functions or pointers to functions

Each Type is an Alpha node by default.

Alpha nodes may have a Tau attribute pointing to another Alpha node; 
this represents the value's location or a pointer to its location.
Alpha nodes may have a Lambda attribute pointing to zero or more Alpha nodes;
this represents the value's argument variables and return variables.
'''

class Type:
    def __init__(self, uf_id):
        # Representative Union-Find ID
        self.uf_id = uf_id

        # A location, or a pointer to a location
        # None if bottom, otherwise another Type
        self.tau_ref = None

        # A function, or a pointer to a function
        # None if bottom, otherwise zero or more Types
        self.lam_args = None 
        self.lam_rets = None

    # Currently unused (could use in unify_ for better for style)
    def is_tau_bottom(self):
        return self.tau_ref is None
    
    def is_lam_bottom(self):
        return self.lam_args is None
    

class TypeManager:
    def __init__(self, uf):
        # The Union-Find instance used for managing Types
        self.uf = uf

        # A dictionary of all Type nodes
        self.nodes = {}

        # The next unused numerical ID for new Type creation
        self.next_id = 0

    # Instantiation of a new Type node
    def new_alpha(self):
        new_id = self.next_id
        self.next_id += 1

        # Add new ID to UF
        self.uf.add(new_id)

        node = Type(new_id)

        # Save Type to manager by new ID
        self.nodes[new_id] = node

        return node