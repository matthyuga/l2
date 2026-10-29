"""Local wrapper/conditional support; never modifies the shared catalog parser."""
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'amber-l2/scripts'))
from contract_dat import Catalog as BaseCatalog


class Catalog(BaseCatalog):
    def read(self, kind):
        if kind in ('INT', 'UBYTE'):
            value = struct.unpack_from('<i' if kind == 'INT' else '<B', self.data, self.offset)[0]
            self.offset += 4 if kind == 'INT' else 1
            return value
        return super().read(kind)

    def parse(self, nodes, variables):
        out = {}
        for node in nodes:
            name = node.get('name')
            if node.tag == 'node':
                out[name] = self.read(node.get('reader'))
                variables[name] = out[name]
            elif node.tag == 'wrapper':
                out.update(self.parse(node, variables))
            elif node.tag == 'if':
                if variables[node.get('param').lstrip('#')] == int(node.get('val')):
                    out.update(self.parse(node, variables))
            elif node.tag == 'for':
                out[name + '_items'] = [self.parse(node, dict(variables))
                                       for _ in range(variables[node.get('size').lstrip('#')])]
            else:
                raise ValueError(node.tag)
        return out

    def encode(self, record, nodes=None):
        out = bytearray()
        for node in self.schema if nodes is None else nodes:
            if node.tag == 'wrapper':
                out += self.encode(record, node)
            elif node.tag == 'if':
                if record[node.get('param').lstrip('#')] == int(node.get('val')):
                    out += self.encode(record, node)
            elif node.tag == 'node' and node.get('reader') in ('INT', 'UBYTE'):
                out += struct.pack('<i' if node.get('reader') == 'INT' else '<B', record[node.get('name')])
            else:
                out += super().encode(record, [node])
        return out
