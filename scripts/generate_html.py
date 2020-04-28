"""
This script generates annotated HTML documents with underlines
showing where collected data applies.
"""

import logging
import sys
import os
import gzip
import json
import collections
import html

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ALL_TYPES = ['full-id', 'source', 'type', 'doc', 'text', 'tactic_params', 'tactic_param_idx', 'state']
TYPE_ABBRS = ['id ', 'src', 'typ', 'doc', 'txt', 'par', 'pid', 'st ']
ABBR_BY_TYPE = {t: a for t, a in zip(ALL_TYPES, TYPE_ABBRS)}
COLORS = ['blue', 'red', 'green', 'orange', 'teal', 'grey', 'maroon', 'lime']
COLOR_BY_TYPE = {t: c for t, c in zip(ALL_TYPES, COLORS)}

# DRAWING_CHARACTERS = "╰─╯ ╵"
# DRAWING_CHARACTERS = "╚═╝ ╹"
# DRAWING_CHARACTERS = "┗━┛ ╹"
# DRAWING_CHARACTERS = "└─┘ ╵"
DRAWING_CHARACTERS = "└─┘ ┴"
# DRAWING_CHARACTERS = "╰─╯ ┴"
# DRAWING_CHARACTERS = "╙─╜ ╨"
# DRAWING_CHARACTERS = "┗━┛ ┸"
# DRAWING_CHARACTERS = "┺━┹─┸"
LEFT_CHAR = DRAWING_CHARACTERS[0]
MIDDLE_CHAR = DRAWING_CHARACTERS[1]
RIGHT_CHAR = DRAWING_CHARACTERS[2]
SPACE_CHAR = DRAWING_CHARACTERS[3]
LONE_CHAR = DRAWING_CHARACTERS[4]

HTML_HEADER = """<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap" rel="stylesheet">
</head>
"""
CODE_STYLE = 'font-family: menlo, "Source Code Pro", monospace;'


class HTMLBuilder:
    def __init__(self):
        self.header = HTML_HEADER
        self.body = []

    def get_html(self):
        return "{}\n<body>\n{}\n</body>".format(self.header, self.wrap_pre("".join(self.body)))

    def save_file(self, path):
        with open(path, "w") as f:
            f.write(self.get_html())

    @staticmethod
    def wrap_code(inner):
        return "<code style='{}'>{}</code>".format(CODE_STYLE, inner)

    @staticmethod
    def wrap_font_color(color, inner):
        return "<font color='{}'>{}</font>".format(color, inner)

    @staticmethod
    def wrap_hover(title, inner):
        return "<a title='{}'>{}</a>".format(html.escape(title, quote=True), inner)

    @staticmethod
    def wrap_pre(inner):
        return "<pre>{}</pre>".format(inner)

    @staticmethod
    def wrap_link(target, inner):
        return "<a href='{}'>{}</a>".format(target, inner)

    def add_file_link(self, target, content):
        self.body.append(self.wrap_link(target, content))
        self.body.append("<br>\n")

    def add_new_line(self):
        self.body.append("\n")

    def add_code_spaces(self, length):
        self.body.append(self.wrap_code(" " * length))

    def add_label(self, label, hovertext):
        labeled = self.wrap_font_color(
            'grey',
            self.wrap_hover(
                hovertext,
                self.wrap_code(label + "  ")
            )
        )

        self.body.append(labeled)

    def add_code_line(self, i, code_line):
        code_html = "{:3}  {}".format(i, html.escape(code_line))
        code_html = self.wrap_code(code_html)
        self.body.append("\n" + code_html)

    @staticmethod
    def underline_string(length, start_group, end_group):
        if length == 1:
            if start_group and end_group:
                return LONE_CHAR
            elif start_group:
                return LEFT_CHAR
            elif end_group:
                return RIGHT_CHAR
            else:
                return MIDDLE_CHAR

        else:
            if start_group:
                start_marker = LEFT_CHAR
            else:
                start_marker = MIDDLE_CHAR

            if end_group:
                end_marker = RIGHT_CHAR
            else:
                end_marker = MIDDLE_CHAR

            return start_marker + MIDDLE_CHAR * (length - 2) + end_marker

    def add_underline(self, color, hovertext, length, start_group, end_group):
        underline = self.wrap_font_color(
            color,
            self.wrap_hover(
                hovertext,
                self.wrap_code(
                    self.underline_string(length, start_group, end_group)
                )
            )
        )
        self.body.append(underline)


def build_marker(current_pos, start, end, start_flag, end_flag, line_width):
    if end is None:
        end = line_width + 2  # Add 2 because of the end-of-line character
        assert start < end, (current_pos, start, end, start_flag, end_flag, line_width)

    marker_string = SPACE_CHAR * (start - current_pos)
    if start + 1 == end:
        if start_flag and end_flag:
            marker_string += LONE_CHAR
        elif start_flag:
            marker_string += LEFT_CHAR
        elif end_flag:
            marker_string += RIGHT_CHAR
        else:
            marker_string += MIDDLE_CHAR

    else:
        if start_flag:
            start_marker = LEFT_CHAR
        else:
            start_marker = MIDDLE_CHAR

        if end_flag:
            end_marker = RIGHT_CHAR
        else:
            end_marker = MIDDLE_CHAR

        marker_string += start_marker + MIDDLE_CHAR * (end - start - 2) + end_marker

    return marker_string


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


def convert_datafile_into_html(data_directory, mathlib_src, lean_library, filename, output_path):
    # get data from file
    data = get_data(data_directory, filename)

    # sort by start_line, type, start_column
    sorted_data = []
    for t, sub_data in data.items():
        for _, item in sub_data.items():
            sorted_data.append((item['line1'], t, item['col1'], item))
    sorted_data.sort()

    # process data to display
    display_data = collections.defaultdict(list)
    for l1, t, c1, item in sorted_data:
        l2 = item['line2']
        c2 = item['col2']

        # handle if goes to the end of the line
        if c2 == 1:
            l2 = l2 - 1
            c2 = None

        start_flag = True
        while l1 <= l2:
            if l1 == l2:
                end_flag = True
                display_data[l1, t].append((c1, c2, start_flag, end_flag, item['info_content']))
            else:
                end_flag = False
                display_data[l1, t].append((c1, None, start_flag, end_flag, item['info_content']))
            l1 += 1
            c1 = 1  # start at the beginning of 1-index line
            start_flag = False

    # get the lines in the file
    if not sorted_data:
        return  # don't bother with files that are only made of comments and have no code

    raw_file = sorted_data[0][3]['file']
    if "/mathlib/src/" in raw_file:
        raw_file = mathlib_src + raw_file.split("/mathlib/src/")[1]
    elif "/lean/library/" in raw_file:
        raw_file = lean_library + raw_file.split("/lean/library/")[1]
    else:
        raise ValueError("Unexpected filename {}".format(raw_file))

    lines = []
    with open(raw_file, "r") as f:
        for l in f:
            lines.append(l[:-1])

    # make html
    html_builder = HTMLBuilder()
    for i, code_line in enumerate(lines):
        l = i + 1
        html_builder.add_code_line(l, code_line)
        for t in ALL_TYPES:
            if (l, t) in display_data:
                html_builder.add_new_line()
                html_builder.add_label(ABBR_BY_TYPE[t], t)
                color = COLOR_BY_TYPE[t]
                c = 1  # start at the beginning of 1-index line
                for c1, c2, start_flag, end_flag, text in display_data[l, t]:
                    if c2 is None:
                        c2 = len(code_line) + 2  # +2 for the new line character
                    html_builder.add_code_spaces(c1 - c)
                    html_builder.add_underline(color, str(text), c2 - c1, start_flag, end_flag)
                    c = c2

    html_builder.save_file(output_path)


def main():
    # command line arguments
    assert len(sys.argv) == 5
    data_directory = sys.argv[1]
    assert os.path.isdir(data_directory)
    mathlib_src = sys.argv[2]
    assert os.path.isdir(mathlib_src)
    lean_library = sys.argv[3]
    assert os.path.isdir(lean_library)
    output_directory = sys.argv[4]
    assert os.path.isdir(output_directory)

    html_files = []
    for filename in os.listdir(data_directory):
        if filename.endswith(".json.gz"):
            logging.info("Processing {}".format(data_directory + filename))
            file_root_name = filename.replace(".json.gz", "")
            output_path = output_directory + filename.replace(".json.gz", ".html")
            convert_datafile_into_html(data_directory, mathlib_src, lean_library, filename, output_path)

            html_files.append((file_root_name, output_path))


if __name__ == "__main__":
    main()
