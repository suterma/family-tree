#!/usr/bin/env bash

# Creates a family tree .svg rendering from .family files.
#
# Optional argument: [path]
# 
# If path is a directory, all .family files in that directory are processed. 
# If path is a .family file, only that file is processed. 
# If no path is given, all .family files in the current directory are processed. #
#
# 1. Uses the family-tree.py script with the custom family DSL as input
# 2. Produces a GraphViz representation as a DOT file
# 3. Tranforms the GraphViz DOT file into an SVG graphic
# 4. Postprocesses the SVG file with custom CSS for visual improvement

# Stop when something goes wrong, including failures inside pipelines.
set -euo pipefail

path="${1:-.}"

# Check that the path exists
if [ ! -e "$path" ]; then
    echo "Error: '$path' does not exist." >&2
    exit 1
fi

# Build the list of family files to process
if [ -f "$path" ]; then
    # A single file was specified
    case "$path" in
        *.family)
            files=("$path")
            ;;
        *)
            echo "Error: '$path' is not a .family file." >&2
            exit 1
            ;;
    esac
elif [ -d "$path" ]; then
    # A directory was specified
    files=("$path"/*.family)

    # Handle directories containing no .family files
    if [ ! -e "${files[0]}" ]; then
        echo "No .family files found in '$path'."
        exit 0
    fi
else
    echo "Error: '$path' is neither a file nor a directory." >&2
    exit 1
fi

for family in "${files[@]}"; do
    base="${family%.family}"

    python3 family-tree.py "$family" \
    | dot -Tsvg \
    | python3 svg_postprocess.py -c family.css \
    > "${base}.svg"
    echo "Produced ${base}.svg"

    # Explicit output for DOT debugging
    # python3 family-tree.py "$family" > "${base}-debug.dot"
    # echo "Produced ${base}-debug.dot"

done

echo "Done."