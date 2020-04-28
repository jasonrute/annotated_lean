import sys
import os
import gzip
import json
import collections

INDEX_HEADER = """# Annotated Lean Files

In each file, hover over the colored lines to get more information.

"""


def get_data(data_directory, filename):
    with gzip.open(data_directory + filename, 'rt') as f:
        t = f.read()
        d = json.loads(t)

    data = collections.defaultdict(dict)
    for item in d:
        info_type = item['info_type']
        pos1 = item['pos1']
        data[info_type][pos1] = item

    return data


def main():
    # command line arguments
    assert len(sys.argv) == 5
    data_directory = sys.argv[1]
    assert os.path.isdir(data_directory)
    git_repo = sys.argv[2]         # e.g. jasonrute/annotated_lean
    html_directory = sys.argv[3]   # e.g. html/
    assert os.path.isdir(html_directory)
    output_file = sys.argv[4]

    # Get versions from data
    def versions():
        for filename in os.listdir(data_directory):
            if filename.endswith(".json.gz"):
                print("Processing {}".format(data_directory + filename))
                data = get_data(data_directory, filename)
                if data:
                    for k in data:
                        for p in data[k]:
                            lean_version = data[k][p]['_lean_version']
                            mathlib_commit = data[k][p]['_mathlib_rev']
                            return lean_version, mathlib_commit

    lean_version, mathlib_commit = versions()


    lean_library_files = []
    mathlib_files = []

    for filename in os.listdir(html_directory):
        if filename.endswith(".html"):
            print("Processing {}".format(html_directory + filename))
            lean_file = filename.replace(".html", ".lean").replace("__", "/")

            if lean_file.startswith("init"):
                lean_library_files.append((lean_file, filename))
            else:
                mathlib_files.append((lean_file, filename))

    lean_library_files.sort()
    mathlib_files.sort()


    with open(output_file, "w") as f:
        f.write(INDEX_HEADER + "\n")

        f.write(f"## [Lean library files](https://github.com/leanprover-community/lean) ([v{lean_version}](https://github.com/leanprover-community/lean/tree/v{lean_version}))\n")
        for lean_file, filename in lean_library_files:
            f.write(f"*  [{lean_file}](https://htmlpreview.github.io/?{git_repo}/{html_directory}{filename})\n")

        f.write("")

        f.write(f"## [mathlib files](https://github.com/leanprover-community/mathlib) ([{mathlib_commit[:7]}](https://github.com/leanprover-community/mathlib/commit/{mathlib_commit}))\n")
        for lean_file, filename in mathlib_files:
            f.write(f"*  [{lean_file}](https://htmlpreview.github.io/?{git_repo}/{html_directory}{filename})\n")

if __name__ == "__main__":
    main()