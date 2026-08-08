#!/usr/bin/env python3

"""
svg_postprocess.py

Postprocess GraphViz SVG output.

- Replace rectangular node polygons with <rect>.
- Preserve existing styling attributes.
- Add class="node-box".
- Removes explicit text styles
- Replaces underscores in text nodes with a space
- Inline styles from an external CSS stylesheet.

Usage:

    python svg_postprocess.py input.svg > output.svg

or

    dot -Tsvg graph.dot | python svg_postprocess.py > graph.svg

Optional:

    python svg_postprocess.py input.svg -c graph.css > output.svg
"""

import argparse
import sys
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

NS = {"svg": SVG_NS}


def parse_points(s):
    pts = []
    for pair in s.strip().split():
        x, y = pair.split(",")
        pts.append((float(x), float(y)))
    return pts


def polygon_is_rectangle(points):
    """
    Detect a rectangle of the form emitted by GraphViz:
    four corners plus repeated first point.
    """
    if len(points) != 5:
        return False

    if points[0] != points[-1]:
        return False

    xs = sorted(set(p[0] for p in points[:-1]))
    ys = sorted(set(p[1] for p in points[:-1]))

    return len(xs) == 2 and len(ys) == 2


def polygon_to_rect(poly):
    points = parse_points(poly.attrib["points"])

    if not polygon_is_rectangle(points):
        return None

    xs = [p[0] for p in points[:-1]]
    ys = [p[1] for p in points[:-1]]

    x = min(xs)
    y = min(ys)
    width = max(xs) - x
    height = max(ys) - y

    rect = ET.Element(f"{{{SVG_NS}}}rect")

    rect.set("x", str(x))
    rect.set("y", str(y))
    rect.set("width", str(width))
    rect.set("height", str(height))

    # preserve style-related attributes
    for attr in (
        "fill",
        "stroke",
        "stroke-width",
        "style",
        "opacity",
    ):
        if attr in poly.attrib:
            rect.set(attr, poly.attrib[attr])

    rect.set("class", "node-box")

    return rect


def insert_css(root, cssfile):
    style = ET.Element(f"{{{SVG_NS}}}style")
    style.set("type", "text/css")

    with open(cssfile, "r", encoding="utf-8") as f:
        style.text = f.read()

    root.insert(0, style)


def process(tree):
    root = tree.getroot()

    # polygon boxes as rects
    for g in root.findall(".//svg:g[@class='node']", NS):

        polygon = g.find("svg:polygon", NS)
        if polygon is None:
            continue

        rect = polygon_to_rect(polygon)
        if rect is None:
            continue

        children = list(g)
        idx = children.index(polygon)

        g.remove(polygon)
        g.insert(idx, rect)

    # cleanup text
    for text in root.findall(".//svg:text", NS):
        text.attrib.pop("font-size", None)
        text.attrib.pop("font-family", None)        

    for text in root.findall(".//svg:text", NS):
        if text.text:
            text.text = text.text.replace("_", " ")        

    return tree


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="-")
    parser.add_argument("-c", "--css", default="graph.css")
    args = parser.parse_args()

    if args.input == "-":
        tree = ET.parse(sys.stdin)
    else:
        tree = ET.parse(args.input)

    tree = process(tree)

    insert_css(tree.getroot(), args.css)

    tree.write(
        sys.stdout.buffer,
        encoding="utf-8",
        xml_declaration=True,
    )


if __name__ == "__main__":
    main()
