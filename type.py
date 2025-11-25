
class Type:
    def __init__(self, uf_id):
        # Representative Union-Find ID
        self.uf_id = uf_id

        # None if bottom, otherwise another AlphaNode
        self.tau_ref = None

        self.lam_args = None 
        self.lam_rets = None

    def is_tau_bottom(self):
        return self.tau_ref is None
    
    def is_lam_bottom(self):
        return self.lam_args is None
    

class TypeManager:
    def __init__(self, uf):
        self.uf = uf
        self.nodes = {}
        self.next_id = 0

    def new_alpha(self):
        new_id = self.next_id
        self.next_id += 1
        self.uf.add(new_id)
        node = Type(new_id)
        self.nodes[new_id] = node
        return node