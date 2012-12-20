#  test_sqlalchemy_nested_set.py
#
#  Created by Jun Kikuchi
#  Copyright (c) 2012 Jun Kikuchi. All rights reserved.
#
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy_nested_set as nested_set

engine  = create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()
class Node(Base, nested_set.Base):
    __tablename__ = 'node'

    def __repr__(self):
        return '<Node(id:%s parent:%s left:%s right: %s)>' %\
            (self.id, self.parent, self.left, self.right)
nested_set.listen(Node)

class NestedSetExtensionTestCase(unittest.TestCase):
    def setUp(self):
        metadata = Base.metadata
        metadata.drop_all(engine)
        metadata.create_all(engine)

    def test_add_root(self):
        session = Session()

        node = Node()
        session.add(node)
        session.flush()

        self.assertEqual(node.parent, None)
        self.assertEqual(node.left, 1)
        self.assertEqual(node.right, 2)

    def test_add_roots(self):
        session = Session()

        node1 = Node()
        node2 = Node()
        node3 = Node()

        session.add(node1)
        session.add(node2)
        session.add(node3)
        session.flush()
        session.expire_all()

        self.assertEqual(node1.parent, None)
        self.assertEqual(node1.left, 1)
        self.assertEqual(node1.right, 2)

        self.assertEqual(node2.parent, None)
        self.assertEqual(node2.left, 3)
        self.assertEqual(node2.right, 4)

        self.assertEqual(node3.parent, None)
        self.assertEqual(node3.left, 5)
        self.assertEqual(node3.right, 6)

if __name__ == "__main__":
    unittest.main()
