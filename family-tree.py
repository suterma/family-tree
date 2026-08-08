#!/usr/bin/env python3

# Parser created by ChatGPT for the custom family-tree DSL.
# It creates GraphViz dot files representing the DSL.

# Usage
# python family-tree.py example.family > example.dot
# dot -Tsvg example.dot -o example.svg

import re
import sys
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    birth: str = ""
    death: str = ""


persons = {}
marriages = []
children = []

person_re = re.compile(
    r'^(.+?)\s*\((\d{4})?(?:-(\d{4})?)?\)\s*$'
)

simple_person_re = re.compile(r'^([A-Za-z0-9_ ]+)$')

marriage_re = re.compile(
    r'^(.+?)\s*\+\s*(.+)$'
)

child_re = re.compile(
    r'^(.+?)\s*<-\s*(.+?),\s*(.+)$'
)

with open(sys.argv[1]) as f:
    for line in f:

        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if m := person_re.match(line):
            name, birth, death = m.groups()
            persons[name] = Person(name, birth or "", death or "")
            continue

        if m := simple_person_re.match(line):
            name = m.group(1)
            persons.setdefault(name, Person(name))
            continue

        if m := marriage_re.match(line):
            marriages.append((m.group(1), m.group(2)))
            continue

        if m := child_re.match(line):
            children.append((m.group(1), m.group(2), m.group(3)))
            continue

        raise ValueError(f"Cannot parse: {line}")

print("digraph Family {")
# Use hierarchy from top to bottom, rectangular connection, try to merge overlapping edges.
print("  graph [" \
"rankdir=TB," \
# Note: Orthogonal splines cause the edge attachment to misbehave, resulting in randomly directed inheritance lines
#"splines=ortho," \
"concentrate=true," \
"ranksep=0.4," \
"nodesep=0.4]")
print("  node [shape=box,style=\"filled\"]")

for p in persons.values():

    label = p.name

    if p.birth or p.death:
        label += "\\n"

        if p.birth:
            label += p.birth

        label += "–"

        if p.death:
            label += p.death

    print(f'  "{p.name}" [label="{label}"];')

marriage_nodes = {}


# Give marriages more weight in the layout if they appear later in the DSL
from itertools import count
marriage_weight = count(100)

for i, (a, b) in enumerate(marriages):

    node = f"m{i}"

    marriage_nodes[frozenset((a, b))] = node

    # Marriage nodes should not be points, to facilitate specific edge attachment
    print(
        f'  {node} [shape=circle,width=0.1,height=0.1,label=""];'
    )

    print(f'  "{a}":s -> {node}:n [dir=none,weight={next(marriage_weight)}];')
    print(f'  "{b}":s -> {node}:n [dir=none,weight={next(marriage_weight)}];')

for child, p1, p2 in children:

    key = frozenset((p1, p2))

    if key not in marriage_nodes:
        raise RuntimeError(
            f"No marriage declared for {p1} and {p2}"
        )

    print(f'  {marriage_nodes[key]}:s -> "{child}":n;')

print("}")
