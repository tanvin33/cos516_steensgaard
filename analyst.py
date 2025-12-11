from union_find import UnionFind


""" 
A TypeNode represents an Alpha type in Steensgaard's analysis. 

It contains a UF ID, and structural information (Tau and Lambda types).
The tau type is represented as another UF ID (the target of a pointer).

"""


class TypeNode:
    def __init__(self, uf_id=None, tau=None, lam=None):
        self.uf_id = uf_id

        # Determine bottom status
        # It is bottom if it has no structural info (tau or lam)
        self.is_bottom = tau is None and lam is None

        self.tau = tau
        self.lam = lam
        self.lam_args = None
        self.lam_rets = None

    def __str__(self):
        return f"TypeNode(uf_id={self.uf_id}, is_bottom={self.is_bottom}, tau={self.tau}, lam={self.lam})"

    def __repr__(self):
        return f"TypeNode(uf_id={self.uf_id}, is_bottom={self.is_bottom}, tau={self.tau}, lam={self.lam})"


"""
The Analyst class does the heavy lifting of Steensgaard's analysis. 
It uses a Union-Find data structure to manage types, based on their UF IDs.

It supports operations to handle different kinds of constraints, such as
assignments, address-of, etc. 
"""


class Analyst:
    def __init__(self):
        # The Union-Find instance used for managing Types
        self.uf = UnionFind()

        # A mapping of UF IDs to TypeNodes (type() in Steensgaard's paper)
        self.nodes = {}

        # A mapping of UF IDs to sets of pending UF IDs
        self.pending = {}

        # The next unused numerical ID for new Type creation
        self.next_id = 0

    # Helper function for finding ECR representatives of UF IDs
    def ecr(self, x):
        # Find representative of x
        return self.uf.find(x)

    # Helper function: get TypeNode for an UF ID
    def node_for(self, x):
        return self.nodes[self.ecr(x)]

    # Instantiation of a new Type node
    def new_type(self, uf_id):
        # Add new ID to UF
        self.uf.add(uf_id)

        node = TypeNode(uf_id)

        # Save TypeNode to manager by new ID
        # Assume ID is variable name
        self.nodes[uf_id] = node

        # Initialize pending set for new ID
        self.pending[uf_id] = set()

        return node

    # e1 and e2 are UF IDs
    def join(self, e1, e2):
        # Get TypeNodes for the equivalence classes of e1 and e2
        e1 = self.ecr(e1)
        e2 = self.ecr(e2)
        t1 = self.nodes[e1]
        t2 = self.nodes[e2]

        # Union e1 and e2
        self.uf.union(e1, e2)
        e = self.uf.find(e1)  # Or return from union()

        if t1.is_bottom:
            self.nodes[e] = t2

            if t2.is_bottom:
                # if both are bottom, merge pending sets
                self.pending[e] = self.pending[e1] | self.pending[e2]
            else:
                # if t2 is not bottom, handle pending set of e1
                for x in self.pending[e1]:
                    self.join(e, x)

        else:
            self.nodes[e] = t1

            if t2.is_bottom:
                # if t1 is not bottom, handle pending set of t2
                for x in self.pending[e2]:
                    self.join(e, x)
            else:
                self.unify(t1, t2)

    # t1 and t2 are TypeNodes
    # TODO: currently only handles tau, need to handle lam too
    def unify(self, t1, t2):
        if t1.tau is not None and t2.tau is not None:
            if t1.tau != t2.tau:
                self.join(t1.tau, t2.tau)
        elif t1.tau is None and t2.tau is not None:
            t1.tau = t2.tau
        elif t2.tau is None and t1.tau is not None:
            t2.tau = t1.tau

        # if len(t1.lam_args) != len(t2.lam_args) or len(t1.lam_rets) != len(t2.lam_rets):
        #     print("ERROR")
        #     # case with different arity (should not happen)
        #     return

        # for i in range(len(t1.lam_args)):
        #     self.join(t1.lam_args[i].uf_id, t2.lam_args[i].uf_id)

        # for i in range(len(t1.lam_rets)):
        #     self.join(t1.lam_rets[i].uf_id, t2.lam_rets[i].uf_id)

    # e1 and e2 are UF IDs
    def cjoin(self, e1, e2):
        print("cjoin", e1, e2)
        t2 = self.nodes[e2]

        if t2.is_bottom:
            print("t2 is bottom, adding pending")
            self.pending[e2] = {e1} | self.pending[e2]
        else:
            print("t2 is not bottom, joining")
            self.join(e1, e2)

    # e1 is a UF ID and t is a TypeNode
    def settype(self, e, t):
        print("Set type", e, "to", t)
        self.nodes[e] = t

        for x in self.pending[e]:
            self.join(e, x)

    def handle_assign(self, x, y):
        # handle the assignment x := y
        e1 = self.ecr(x)
        e2 = self.ecr(y)
        t1 = self.nodes[e1]
        t2 = self.nodes[e2]

        print("Handling assign:", x, y)
        print("Types before:", t1, t2)
        print("Taus before:", t1.tau, t2.tau)

        if t1.tau != t2.tau:
            print("Assign, taus not equal")
            self.cjoin(self.ecr(t1.tau), self.ecr(t2.tau))

    def handle_addr_of(self, x, y):
        # handle the assignment x := &y
        print("Handling address of:", x, y)

        e1 = self.ecr(x)
        tau_2 = self.ecr(y)
        t1 = self.nodes[e1]

        # If t1 is ⊥, set its type to point to e2 (and make it non-bottom)
        if t1.is_bottom:
            t1.tau = tau_2
            t1.is_bottom = False
            # Satisfy any pending assignments on e1
            self.settype(e1, t1)

        print("EQR:", e1, tau_2)
        print("Taus before:", t1.tau, tau_2)

        if t1.tau != tau_2:
            self.join(t1.tau, tau_2)

    def handle_deref(self, x, y):
        # x := *y
        e2 = self.ecr(y)
        t2 = self.nodes[e2]
        tau_2 = t2.tau

        e1 = self.ecr(x)
        t1 = self.nodes[e1]

        if tau_2 is None:
            # y has no target, but in order to deref, it must point to something
            print("Deref: y has no target.")
            fresh_var = self.next_id
            self.next_id += 1
            self.new_type(fresh_var)  # Register new var in UF
            t2.tau = fresh_var
            t2.is_bottom = False
            tau_2 = t2.tau

        # if y is bottom, create a fresh varaible as its "target"
        if self.nodes[tau_2].is_bottom:
            self.settype(tau_2, t1)
        else:
            t3 = self.nodes[tau_2]
            if t3.tau != t1.tau:
                self.cjoin(t1.tau, t3.tau)

    def handle_op(self, x, operands):
        e_x = self.ecr(x)
        t_x = self.nodes[e_x]
        # x := op(...)
        for operand in operands:
            print("Operand:", operand)
            e_yi = self.ecr(operand)
            t_yi = self.nodes[e_yi]
            print("c-Joining", t_x.tau, "and", t_yi.tau)
            if t_x.tau != t_yi.tau:
                self.cjoin(t_x.tau, t_yi.tau)

    def handle_allocate(self, x):
        # x := allocate()
        e_x = self.ecr(x)
        t_x = self.nodes[e_x]
        x_target = t_x.tau
        if x_target is None:
            return
        if self.nodes[x_target].is_bottom:
            fresh_var_1 = self.next_id
            self.next_id += 1
            self.new_type(fresh_var_1)  # Register new var in UF

            fresh_var_2 = self.next_id
            self.next_id += 1
            self.new_type(fresh_var_2)  # Register new var in UF

            new_type = TypeNode(self.next_id, tau=fresh_var_1, lam=[fresh_var_2])
            self.next_id += 1

            self.settype(x_target, new_type)
            t_x.is_bottom = False
