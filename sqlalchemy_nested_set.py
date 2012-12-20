#  sqlalchemy_nested_set.py
#
#  Created by Jun Kikuchi
#  Copyright (c) 2012 Jun Kikuchi. All rights reserved.
#
from sqlalchemy import Column, Integer, select, func, case, event

class Base():
    __mapper_args__ = {
        'batch': False
    }

    id     = Column(Integer, primary_key=True)
    parent = Column(Integer)
    left   = Column('lft', Integer, nullable=False)
    right  = Column('rgt', Integer, nullable=False)

def before_insert_listener(mapper, connection, instance):
    table = mapper.mapped_table
    max_right = connection.scalar(
        select(
            [func.max(table.c.rgt)],
            table.c.parent == instance.parent
        )
    ) or 0

    connection.execute(
        table.update(table.c.rgt >= max_right).values(
            lft = case(
                [(table.c.lft > max_right, table.c.lft + 2)],
                else_ = table.c.lft
            ),
            rgt = case(
                [(table.c.rgt > max_right, table.c.rgt + 2)],
                else_ = table.c.rgt
            )
        )
    )

    instance.left  = max_right + 1
    instance.right = max_right + 2

def before_delete_listener(mapper, connection, instance):
    shift = (instance.right - instance.left) + 1

    table = mapper.mapped_table
    connection.execute(
        table.update().values(
            lft = case(
                [(table.c.lft > instance.left,  table.c.lft - shift)],
                else_ = table.c.lft
            ),
            rgt = case(
                [(table.c.rgt > instance.right, table.c.rgt - shift)],
                else_ = table.c.rgt
            )
        )
    )

def listen(node_class):
    event.listen(node_class, 'before_insert', before_insert_listener)
    event.listen(node_class, 'before_delete', before_delete_listener)
