import unittest
from parse import Node

test_node: dict = {
              "opcItemPath": {
                "bindType": "parameter",
                "binding": "{Device01}.105.24:136"
              },
              "historyProvider": {
                "bindType": "parameter",
                "binding": "{History Provider}"
              },
              "opcServer": {
                "bindType": "parameter",
                "binding": "{Server}"
              },
              "valueSource": "opc",
              "dataType": "Float4",
              "historicalDeadbandStyle": "Discrete",
              "historyEnabled": True,
              "name": "Run Time Today",
              "enabled": True,
              "engUnit": "psi",
              "tagType": "AtomicTag"
            }

class NodeTest(unittest.TestCase):
    def test_name(self):
        self.assertEqual(test_node['name'], Node.from_dict(test_node, '').name)

if __name__ == '__main__':
    unittest.main()
