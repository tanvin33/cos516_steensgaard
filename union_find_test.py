'''
Unit tests for the UnionFind class.
'''
import unittest
from union_find import UnionFind

class UnionFindTest(unittest.TestCase):

  def test_add(self):
    uf = UnionFind()
    uf.add('x')
    sets = uf.get_sets()
    self.assertEqual(len(sets), 1)
    self.assertEqual(sets[0], ['x'])
    
    uf.add('y')
    sets = uf.get_sets()
    self.assertEqual(len(sets), 2)
    self.assertIn(['x'], sets)
    self.assertIn(['y'], sets)

    uf.add('x')  # Adding existing item should not change sets
    sets = uf.get_sets()
    self.assertEqual(len(sets), 2)
  
  def test_find(self):
    uf = UnionFind()
    uf.add('a')
    uf.add('b')
    self.assertEqual(uf.find('a'), 'a')
    self.assertEqual(uf.find('b'), 'b')
    
    uf.union('a', 'b')
    self.assertEqual(uf.find('a'), uf.find('b'))
  
  def test_union(self):
    uf = UnionFind()
    uf.add('a')
    uf.add('b')
    uf.union('a', 'b')
    sets = uf.get_sets()
    self.assertEqual(len(sets), 1)
    self.assertEqual(sets, [['a', 'b']])
    
    elements = ['c', 'd', 'e']
    for el in elements:
        uf.add(el)
    uf.union('c', 'd')
    sets = uf.get_sets()
    expected_sets = [['a', 'b'], ['c', 'd'], ['e']]
    self.assertEqual(len(sets), 3)
    for s in expected_sets:
        self.assertIn(s, sets)

  def test_str(self):
    uf = UnionFind()
    uf.add('x')
    uf.add('y')
    uf.union('x', 'y')
    parent_str = str(uf)
    self.assertEqual("{'x': 'x', 'y': 'x'}", parent_str)

if __name__ == '__main__':
    unittest.main()