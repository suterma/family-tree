# family-tree
Using a simple domain specific language ([DSL](https://en.wikipedia.org/wiki/Domain_specific_language)), the _family-tree_ python script parses `.family` files into a [_GraphViz_](https://graphviz.org/) DOT file, then renders the family tree as an [SVG](https://en.wikipedia.org/wiki/SVG) graphic.

![Example family tree rendering](./examples/example.svg "Example familty tree")

## Overview
The _family-tree_ domain specific language (DSL) supports 3 concepts:

- Persons (with optional birth and death years)
- Marriages
- Children

## Prerequisites

- [_Python_](https://www.python.org/downloads/) installed
- [_GraphViz_](https://graphviz.org/)  installed

```console
sudo apt install python3
sudo apt install graphviz
```

## Usage

```console
./produce.sh ./examples/example.family
```

1. Uses the family-tree.py script with the custom family DSL as input
2. Produces a GraphViz representation as a DOT file
3. Tranforms the GraphViz DOT file into an SVG graphic
4. Postprocesses the SVG file with custom CSS for visual improvement

## Family DSL

_family-tree_ uses a small domain specific language (DSL). It describes people and their relationships using a few simple rules.

Example input (from `./examples/example.family`):

```text
# Persons
Anton (1950-2020)
Antoinette (1952-)

Bertrand (1978)
Claire (1980)

Sophie_Smith (1981)

Emma (2008-)

# Marriages
Anton + Antoinette
Bertrand + Sophie_Smith

# Children
Bertrand <- Anton, Antoinette
Claire    <- Anton, Antoinette
Emma       <- Bertrand, Sophie_Smith
```

Lines starting with `#` are comments for convenience. It is disregarded by the parser.


### 1. Persons


Each person has this general form:

`Name (birth-death)`

For example:

`Anton (1950-2020)`

means:

- Person: Anton
- Born: 1950
- Died: 2020

A missing date has a special meaning:

`Antoinette (1952-)`

means Antoinette was born in 1952 and is still living (or, more precisely, that no death year is specified).

Similarly:

`Emma (2008-)`

means born in 2008, with no death year specified.

If there is only one year:

`Bertrand (1978)`

then only the birth year is specified; there is no death year.

### 2. Marriages

The `+` means married/partners.

`Anton + Antoinette`

means: Anton and Antoinette are a couple.

And:

`Bertrand + Sophie_Smith`

means: Bertrand and Sophie Smith are a couple.

### 3. Children

`Bertrand <- Anton, Antoinette`

The `<-` can be read as "is the child of"; Bertrand is the child of Anton and Antoinette.

Likewise:

`Claire <- Anton, Antoinette`

means: Claire is the child of Anton and Antoinette.

And:

`Emma <- Bertrand, Sophie_Smith`

means: Emma is the child of Bertrand and Sophie Smith.

### Putting it all together

The file describes the above example family:

- Anton and Antoinette are a couple.
- They have two children: Bertrand and Claire.
- Bertrand and Sophie Smith are a couple.
- They have a child, Emma.
- The numbers in parentheses give birth/death information.

So the DSL is essentially a compact way of saying:

Who are the people? When were they born/did they die? Who is married to whom? Who are whose children?

The _family-tree_ python script parses these human-friendly statements and converts them into a representation that can ultimately be turned into a Graphviz diagram.

### Notes and limitations

Compared to fully fleged family tree software like [_Gramps_](https://gramps-project.org/) or others that support the more complex [GEDCOM](https://en.wikipedia.org/wiki/GEDCOM) format, the _family-tree_ script aims for simplicity.

- Names must always be exactly the same in all three parts, they are essentially technical identifiers
- Spaces are not supported, thus underscores are used to concatenate name parts. They are removed in the postprocessing step.
- To have children, a couple need to have a marriage defined
- The order of the entries in the `.family` files have no specific meaning, except
   - Marriages that are occuring later in the file, have a stronger weight in GraphViz, resulting in potentially shorter connector lines
- You can concatenate small `.family` files to on larger file to create larger trees. However, remove any duplicate lines in the process.

