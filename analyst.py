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

        # List of TypeNodes
        self.lam_args = []
        self.lam_rets = []

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

    def fresh_type(self):
        new_id = self.next_id
        self.next_id += 1
        return self.new_type(new_id)  # Register new type in UF

    # e1 and e2 are UF IDs
    def join(self, e1, e2):
        t1 = self.nodes[e1]
        t2 = self.nodes[e2]

        e = self.uf.union(e1, e2)

        if t1.is_bottom:
            # self.nodes[e] = t2
            self.assign_type(e, t2)

            if t2.is_bottom:
                self.pending[e] = self.pending[e1] | self.pending[e2]
            else:
                for x in self.pending[e1]:
                    self.join(e, x)
        else:
            # self.nodes[e] = t1
            self.assign_type(e, t1)

            if t2.is_bottom:
                for x in self.pending[e2]:
                    self.join(e, x)
            else:
                self.unify_tau(t1, t2)

    # t1 and t2 are TypeNodes
    def unify_tau(self, type_e1, type_e2):
        tau1 = self.get_tau(type_e1)
        lam1 = self.get_lam(type_e1)

        tau2 = self.get_tau(type_e2)
        lam2 = self.get_lam(type_e2)

        if tau1 != tau2:
            self.join(tau1, tau2)

        if lam1 != lam2:
            self.join(lam1, lam2)

    def unify_lam(self, type_e1, type_e2):
        lam_args_e1 = type_e1.lam_args
        lam_args_e2 = type_e2.lam_args

        for i in range(len(lam_args_e1)):
            tau1 = self.get_tau(lam_args_e1[i])  # self.get_tau(lam_args_e1[i].uf_id)
            lam1 = self.get_lam(lam_args_e1[i])

            tau2 = self.get_tau(lam_args_e2[i])
            lam2 = self.get_lam(lam_args_e2[i])

            if tau1 != tau2:
                self.join(tau1, tau2)

            if lam1 != lam2:
                self.join(lam1, lam2)

        lam_rets_e1 = type_e1.lam_rets
        lam_rets_e2 = type_e2.lam_rets

        for i in range(len(lam_rets_e1)):
            tau1 = self.get_tau(lam_rets_e1[i])  # self.get_tau(lam_args_e1[i].uf_id)
            lam1 = self.get_lam(lam_rets_e1[i])

            tau2 = self.get_tau(lam_rets_e2[i])
            lam2 = self.get_lam(lam_rets_e2[i])

            if tau1 != tau2:
                self.join(tau1, tau2)

            if lam1 != lam2:
                self.join(lam1, lam2)

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
        type_e2 = self.nodes[e2]

        if type_e2.is_bottom:
            print("t2 is bottom, adding pending")
            self.pending[e2] = {e1} | self.pending[e2]
        else:
            print("t2 is not bottom, joining")
            self.join(e1, e2)

    # TODO: MUST: figure out which of the following options produces
    # the right shape graph!!!
    def assign_type(self, e, t):
        type_e = self.nodes[e]
        type_e.tau = t.tau
        type_e.lam = t.lam
        type_e.lam_args = t.lam_args
        type_e.lam_rets = t.lam_rets
        # self.pending[e] = self.pending[self.ecr(t.uf_id)]

    # Or alternatively just return t
    # return t
    """
    def assign_type(self, e, t):
        type_e = self.new_type(e)
        type_e.tau = t.tau
        type_e.lam = t.lam
        return type_e

        # Or alternatively just return t
        #return t
    """

    # e1 is a UF ID and t is a TypeNode with properties we want to copy over.
    def settype(self, e, t):
        print("Set type", e, "to", t)

        # self.nodes[e] = self.assign_type(e, t)

        self.assign_type(e, t)

        for x in self.pending[e]:
            self.join(e, x)

    # Helper function for getting a tau reference from a type
    def get_tau(self, type_):
        if type_.tau is None:
            type_.tau = self.fresh_type().uf_id
        return type_.tau

    def handle_assign(self, x, y):
        # handle the assignment x := y
        ecr_x = self.ecr(x)
        type_x = self.nodes[ecr_x]
        tau1 = self.get_tau(type_x)
        lam1 = type_x.lam

        ecr_y = self.ecr(y)
        type_y = self.nodes[ecr_y]
        tau2 = self.get_tau(type_y)
        lam2 = type_y.lam

        print("Handling assign:", x, y)
        print("Types before:", type_x, type_y)
        print("Taus before:", type_x.tau, type_y.tau)

        if tau1 != tau2:
            print("Assign, taus not equal")
            self.cjoin(tau1, tau2)

        if lam1 != lam2:
            self.cjoin(lam1, lam2)

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
        lam1 = type_x.lam

        ecr_y = self.ecr(y)
        type_y = self.nodes[ecr_y]
        tau2 = self.get_tau(type_y)

        type_tau2 = self.nodes[tau2]

        if type_tau2.is_bottom:
            self.settype(tau2, type_x)
        else:
            tau3 = self.get_tau(type_tau2)
            lam3 = type_tau2.lam
            if tau1 != tau3:
                self.cjoin(tau1, tau3)
            if lam1 != lam3:
                self.cjoin(lam1, lam3)

    def handle_op(self, x, operands):
        for y in operands:
            ecr_x = self.ecr(x)
            type_x = self.nodes[ecr_x]
            tau1 = self.get_tau(type_x)
            lam1 = type_x.lam

            ecr_y = self.ecr(y)
            type_y = self.nodes[ecr_y]
            tau2 = self.get_tau(type_y)
            lam2 = type_y.lam

            if tau1 != tau2:
                self.cjoin(tau1, tau2)
            if lam1 != lam2:
                self.cjoin(lam1, lam2)

    # Make a dummy type to store new ECRs for allocate()
    def make_ecr_type(self):
        return self.fresh_type()
        # type_ = TypeNode("_")
        # type_.tau = self.fresh_type().uf_id
        # type_.lam = self.fresh_type().uf_id
        # return type_

        # type_ = self.fresh_type()
        # type_.tau = self.fresh_type().uf_id
        # type_.lam = self.fresh_type().uf_id
        # return type_

        """
        e1 = self.next_id
        self.next_id += 1
        self.new_type(e1)

        # TODO: Lambda too

        type_ = TypeNode("_")
        type_.tau = e1
        return type_
        """

    def handle_allocate(self, x):
        # x := allocate()
        ecr_x = self.ecr(x)
        type_x = self.nodes[ecr_x]
        tau = self.get_tau(type_x)

        if self.nodes[tau].is_bottom:
            self.settype(tau, self.make_ecr_type())

    def handle_store(self, x, y):
        ecr_x = self.ecr(x)
        type_x = self.nodes[ecr_x]
        tau1 = self.get_tau(type_x)

        ecr_y = self.ecr(y)
        type_y = self.nodes[ecr_y]
        tau2 = self.get_tau(type_y)
        lam2 = type_y.lam

        type_tau1 = self.nodes[tau1]

        if type_tau1.is_bottom:
            self.settype(tau1, type_y)
        else:
            tau3 = self.get_tau(type_tau1)
            lam3 = type_tau1.lam
            if tau2 != tau3:
                self.cjoin(tau3, tau2)
            if lam2 != lam3:
                self.cjoin(lam3, lam2)

    # Helper function for getting a lambda reference from a type
    def get_lam(self, type_):
        if type_.lam is None:  # if x has no lambda value
            type_.lam = self.fresh_type().uf_id
        return type_.lam

    def get_alpha(self, e):
        if e not in self.nodes:
            # e = self.fresh_type().uf_id
            self.new_type(e)
        return e

    def make_lam_type(self, args, rets):
        # TODO: Figure out if type should be fresh (calls new_type,
        # ends up in nodes) or should just be dummy type for copying,
        # based conclusions about the assign_type() correct implementation

        # Currently it seems more elegant to call fresh_type here, and then
        # change assign_type to return t without calling new_type.

        # type_ = self.fresh_type()
        # type_.lam_args = args
        # type_.lam_rets = rets

        # return type_

        type_ = TypeNode("_")
        type_.lam_args = args
        type_.lam_rets = rets
        return type_

    # Must create alpha nodes, then refer to them by ECR
    def handle_fun_def(self, x, f, r):
        ecr_x = self.ecr(x)
        type_x = self.nodes[ecr_x]

        lam = self.get_lam(type_x)
        type_lam = self.nodes[lam]  # This requires lam to be added to nodes

        if type_lam.is_bottom:
            alpha_f = []
            alpha_r = []

            for f_i in f:
                alpha_f_i = self.get_alpha(f_i)
                alpha_f.append(alpha_f_i)

            for r_i in r:
                alpha_r_i = self.get_alpha(r_i)
                alpha_r.append(alpha_r_i)

            # TODO: Should not store ECRs but actual nodes
            self.settype(lam, self.make_lam_type(alpha_f, alpha_r))

        else:
            # lam_args = type_lam.lam_args
            # lam_rets = type_lam.lam_rets

            for i in range(len(f)):
                alpha_i = type_lam.lam_args[i]
                tau1 = self.get_tau(alpha_i)
                lam1 = self.get_lam(alpha_i)

                ecr_f_i = self.ecr(f[i])
                type_f_i = self.nodes[ecr_f_i]
                tau2 = self.get_tau(type_f_i)
                lam2 = self.get_lam(type_f_i)

                # Note distinct order below
                if tau1 != tau2:
                    self.join(tau2, tau1)

                if lam1 != lam2:
                    self.join(lam2, lam1)

            for i in range(len(r)):
                alpha_i = type_lam.lam_rets[i]
                tau1 = self.get_tau(alpha_i)
                lam1 = self.get_lam(alpha_i)

                ecr_r_i = self.ecr(r[i])
                type_r_i = self.nodes[ecr_r_i]
                tau2 = self.get_tau(type_r_i)
                lam2 = self.get_lam(type_r_i)

                # Note distinct order above
                if tau1 != tau2:
                    self.join(tau1, tau2)

                if lam1 != lam2:
                    self.join(lam1, lam2)

    def handle_fun_app(self, x, p, y):
        ecr_p = self.ecr(p)
        type_p = self.nodes[ecr_p]

        lam = self.get_lam(type_p)
        type_lam = self.nodes[lam]

        if type_lam.is_bottom:
            alpha_args = []
            alpha_rets = []

            for i in y:
                alpha_i = self.make_ecr_type()
                alpha_args.append(alpha_i)

            for i in x:
                alpha_i = self.make_ecr_type()
                alpha_rets.append(alpha_i)

            # Just carry over the args and rets instead.
            # TODO FIX BELOW
            # self.settype(lam, self.make_lam_type(alpha_args))

            """
            alpha_args = []

            for i in y:
                alpha_i = self.make_ecr_type()
                alpha_args.append(alpha_i)

            self.settype(lam, self.make_lam_type(alpha_args))
            """

        lam_args = type_lam.lam_args
        lam_rets = type_lam.lam_rets

        for i in range(len(lam_args)):
            alpha_i = lam_args[i]
            tau1 = self.get_tau(alpha_i)
            lam1 = self.get_lam(alpha_i)

            ecr_y_i = self.ecr(y[i])
            type_y_i = self.nodes[ecr_y_i]
            tau2 = self.get_tau(type_y_i)
            lam2 = self.get_lam(type_y_i)

            if tau1 != tau2:
                self.cjoin(tau1, tau2)

            if lam1 != lam2:
                self.cjoin(lam1, lam2)

        for i in range(len(lam_rets)):
            alpha_i = lam_args[i]
            tau1 = self.get_tau(alpha_i)
            lam1 = self.get_lam(alpha_i)

            ecr_x_i = self.ecr(x[i])
            type_x_i = self.nodes[ecr_x_i]
            tau2 = self.get_tau(type_x_i)
            lam2 = self.get_lam(type_x_i)

            if tau1 != tau2:
                self.cjoin(tau2, tau1)

            if lam1 != lam2:
                self.cjoin(lam2, lam1)
