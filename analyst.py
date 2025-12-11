from union_find import UnionFind


class TypeNode:
    """
    A TypeNode represents an Alpha type in Steensgaard's analysis.

    It contains a UF ID, and structural information (Tau and Lambda types).
    The tau type is represented as another UF ID (the target of a pointer).

    """

    def __init__(self, uf_id=None, tau=None, lam=None):
        self.uf_id = uf_id

        self.tau = tau
        self.lam = lam
        self.lam_args = None
        self.lam_rets = None

    @property
    def is_bottom(self):
        return self.tau is None and self.lam is None

    def __str__(self):
        return f"TypeNode(uf_id={self.uf_id}, is_bottom={self.is_bottom}, tau={self.tau}, lam={self.lam})"

    def __repr__(self):
        return f"TypeNode(uf_id={self.uf_id}, is_bottom={self.is_bottom}, tau={self.tau}, lam={self.lam})"


class Analyst:
    """
    The Analyst class does the heavy lifting of Steensgaard's analysis.
    It uses a Union-Find data structure to manage types, based on their UF IDs.

    It supports operations to handle different kinds of constraints, such as
    assignments, address-of, etc.
    """

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
    def unify(self, t1, t2):
        if t1.tau is not None and t2.tau is not None:
            if t1.tau != t2.tau:
                self.join(t1.tau, t2.tau)
        elif t1.tau is None and t2.tau is not None:
            t1.tau = t2.tau
        elif t2.tau is None and t1.tau is not None:
            t2.tau = t1.tau

        # TODO: unify lambda types as well, currently not handled

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

        type_e = self.new_type(e)

        type_e.tau = t.tau

        # TODO: Lambda too

        for x in self.pending[e]:
            self.join(e, x)

    # Create a type to represent an implicit points-to relation (reference) from type t1
    def resolve_tau(self, type_):
        new_id = self.next_id
        self.next_id += 1
        self.new_type(new_id)  # Register new type in UF
        type_.tau = new_id

    # Helper function for getting a tau reference from a type
    def get_tau(self, type_):
        if type_.tau is None:
            self.resolve_tau(type_)
        return type_.tau

    def handle_assign(self, x, y):
        # handle the assignment x := y
        ecr_x = self.ecr(x)
        type_x = self.nodes[ecr_x]
        tau1 = self.get_tau(type_x)

        ecr_y = self.ecr(y)
        type_y = self.nodes[ecr_y]
        tau2 = self.get_tau(type_y)

        print("Handling assign:", x, y)
        print("Types before:", type_x, type_y)
        print("Taus before:", type_x.tau, type_y.tau)

        if tau1 != tau2:
            print("Assign, taus not equal")
            self.cjoin(tau1, tau2)

    def handle_addr_of(self, x, y):
        # handle the assignment x := &y
        print("Handling address of:", x, y)

        ecr_x = self.ecr(x)
        type_x = self.nodes[ecr_x]
        tau1 = self.get_tau(type_x)

        tau2 = self.ecr(y)

        print("ECR:", ecr_x, tau2)
        print("Taus before:", type_x.tau, tau2)

        if tau1 != tau2:
            self.join(tau1, tau2)

    def handle_deref(self, x, y):
        # x := *y
        ecr_x = self.ecr(x)
        type_x = self.nodes[ecr_x]
        tau1 = self.get_tau(type_x)

        ecr_y = self.ecr(y)
        type_y = self.nodes[ecr_y]
        tau2 = self.get_tau(type_y)

        type_tau2 = self.nodes[tau2]

        if type_tau2.is_bottom:
            self.settype(tau2, type_x)
        else:
            tau3 = self.get_tau(type_tau2)
            if tau1 != tau3:
                self.cjoin(tau1, tau3)
            # TODO Lambda as well

    def handle_op(self, x, operands):
        for y in operands:
            ecr_x = self.ecr(x)
            type_x = self.nodes[ecr_x]
            tau1 = self.get_tau(type_x)

            ecr_y = self.ecr(y)
            type_y = self.nodes[ecr_y]
            tau2 = self.get_tau(type_y)

            if tau1 != tau2:
                self.cjoin(tau1, tau2)
            
            # TODO: Lambdas too

    # Make a dummy type to store new ECRs for allocate()
    def make_ecr_type(self):
        e1 = self.next_id
        self.next_id += 1
        self.new_type(e1)

        # TODO: Lambda too

        type_ = TypeNode("_")
        type_.tau = e1
        return type_

    def handle_allocate(self, x):
        # x := allocate()
        ecr_x = self.ecr(x)
        type_x = self.nodes[ecr_x]
        tau = self.get_tau(type_x)

        if self.nodes[tau].is_bottom:
            self.settype(tau, self.make_ecr_type())
