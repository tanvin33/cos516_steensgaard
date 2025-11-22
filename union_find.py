'''
Code for the Union-Find data structure to be used in Steensgaard's analysis.

Usage (For quick sanity check test):
    python union_find.py
'''

class UnionFind:
    """ A Union-Find data structure to maintain equivalence classes. """
    def __init__(self): 
        self.parent = {}
    
    def add(self, item):
        """Adds a new item as its own parent (new set)."""
        if item not in self.parent:
            self.parent[item] = item
    
    def find(self, item):
        """Finds the top element of the set containing 'item'."""
        if self.parent[item] == item:
            return item
        else:
            return self.find(self.parent[item])
    
    def union(self, item1, item2):
        """Unites the sets containing 'item1' and 'item2'."""
        root1 = self.find(item1)
        root2 = self.find(item2)
        if root1 != root2:
            self.parent[root2] = root1
    
    def get_sets(self):
        """Returns all sets in the union-find structure."""
        sets = {}
        for item in self.parent:
            root = self.find(item)
            if root not in sets:
                sets[root] = []
            sets[root].append(item)
        return list(sets.values())
    
    def __str__(self):
        return str(self.parent)
    
def main():
    "Run a simple test of the Union-Find data structure."
    uf = UnionFind()
    elements = ['a', 'b', 'c', 'd', 'e']
    for el in elements:
        uf.add(el)
    print("Initial parent:", uf)
    print("Initial sets:", uf.get_sets())

    uf.union('a', 'b')
    uf.find('b')
    print("After union(a, b):", uf)
    uf.union("d", "e")
    uf.union("b", "d")
    print("After union(d, e) and union(b, d):", uf)
    print("Final sets:", uf.get_sets())

    print("Set with e:", uf.find('e'))
    print("Set with a:", uf.find('a'))
    print("Set with c:", uf.find('c'))

    print("Union-Find test completed.")
        

if __name__ == "__main__":
    "Call the main function to run sanity-check test"
    main()