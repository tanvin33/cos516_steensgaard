from union_find import UnionFind


class TypeNode:
    def __init__(self, uf_id):
        # Union-Find ID
        self.uf_id = uf_id

        # Defaults to bottom
        self.is_bottom = True

        # None if bottom; otherwise, another TypeNode
        self.tau = None

        # None if bottom; otherwise, zero or more TypeNodes
        self.lam_args = None
        self.lam_rets = None


# Helpful information for following from Steensgaard's paper:
# every time Steensgaard calls type(e) we use self.nodes[e]
# where e is a UF ID


class Analyst:
    def __init__(self):
        # The Union-Find instance used for managing Types
        self.uf = UnionFind()

        # A mapping of UF IDs to nodes
        self.nodes = {}

        # A mapping of UF IDs to sets of pending UF IDs
        self.pending = {}

    # Helper function for finding ECR representatives
    def rep(self, x):
        if isinstance(x, TypeNode):
            x = x.uf_id
        return self.uf.find(x)

    # Helper function: get TypeNode for an id or TypeNode
    def node_for(self, x):
        return self.nodes[self.rep(x)]

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

    def join(self, e1, e2):
        t1 = self.node_for(e1)
        t2 = self.node_for(e2)

        # Union e1 and e2
        self.uf.union(e1, e2)
        e = self.uf.find(e1)  # Or return from union()

        if t1.is_bottom:
            self.nodes[e] = t2

            if t2.is_bottom:
                self.pending[e] = self.pending[e1] | self.pending[e2]
            else:
                for x in self.pending[e1]:
                    self.join(e, x)

        else:
            self.nodes[e] = t1

            if t2.is_bottom:
                for x in self.pending[e2]:
                    self.join(e, x)
            else:
                self.unify(t1, t2)

    def unify(self, t1, t2):
        if t1.tau != t2.tau:
            self.join(t1.tau, t2.tau)

        # if len(t1.lam_args) != len(t2.lam_args) or len(t1.lam_rets) != len(t2.lam_rets):
        #     print("ERROR")
        #     # case with different arity (should not happen)
        #     return

        # for i in range(len(t1.lam_args)):
        #     self.join(t1.lam_args[i].uf_id, t2.lam_args[i].uf_id)

        # for i in range(len(t1.lam_rets)):
        #     self.join(t1.lam_rets[i].uf_id, t2.lam_rets[i].uf_id)

    def cjoin(self, e1, e2):
        t2 = self.nodes[e2]

        if t2.is_bottom:
            self.pending[e2] = {e1} | self.pending[e2]
        else:
            self.join(e1, e2)

    def settype(self, e, t):
        self.nodes[e] = t

        for x in self.pending[e]:
            self.join(e, x)

    def handle_assign(self, x, y):
        # handle the assignment x := y
        e1 = self.rep(x)
        e2 = self.rep(y)
        t1 = self.nodes[e1]
        t2 = self.nodes[e2]

        print("Handling assign:", x, y)
        print("Types before:", t1, t2)
        print("Taus before:", t1.tau, t2.tau)

        if t1.tau != t2.tau:
            self.cjoin(t1.tau, t2.tau)

    def handle_addr_of(self, x, y):
        # handle the assignment x := &y
        print("Handling address of:", x, y)

        e1 = self.rep(x)
        e2 = self.rep(y)
        t1 = self.nodes[e1]

        # If t1 is ⊥, set its type to point to e2 (and make it non-bottom)
        if t1.is_bottom:
            t1.tau = e2
            t1.is_bottom = False
            # Satisfy any pending assignments on e1
            self.settype(e1, t1)

        print("EQR:", e1, e2)
        print("Taus before:", t1.tau, e2)

        if t1.tau != e2:
            self.join(e1, e2)
