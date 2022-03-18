from os import path
from re import finditer, search
from sys import argv

# TODO:
# |-- Possibly refactor everything to build an intermediate representation
# |   instead of converting the input to output in-place.
# |   `-- This would also improve performace drastically, I presume.
# |-- Mark lines that were made empty as removable from final output.
# |-- Parse HTML comments and replace them with nothing in final output
# |   ie. `<!-- ... the comment ... -->`
# |-- Horizontal Rules (`---`, `___`, and `***`)
# `-- Parse markdown tables into GNU Texinfo multitables

def print_usage():
    print("Markdown to GNU Texinfo Converter by Rylan `Lens` Kellogg")
    print()
    print("Usage:")
    print("    python main.py [FLAGS] [OPTIONS] \"path/to/markdown.md\"")
    print()
    print("Flags:")
    print("    -h, --help     -- Show the help dialog in stdout")
    print("    -i, --inline   -- Do not specify new nodes for sections within chapters.")
    print("    --hide-toc     -- Hide any line that starts with `#` and contains `Table of Contents`.")
    print()
    print("Options:")
    print("    -t <title>     -- Specify the title of the Texinfo manual that is generated")
    print("    -o <path>      -- Specify the file path where the Texinfo manual will be saved to")
    print()
    exit(0)

def parse_headers_new(src, title, inline, hide_toc):
    lines = src.split('\n')
    within_toc = False
    prev_hash_count = 0
    nest_level = 0
    for i in range(len(lines)):
        if len(lines[i]) < 2:
            continue

        if i == 0 and lines[0][0] == '#' and lines[0][1] == ' ':
            title = lines[0][2:]
            lines[0] = ""
            continue

        if hide_toc and ("table of contents" in lines[i].lower() \
                         or "table-of-contents" in lines[i].lower()):
            lines[i] = ""
            within_toc = True
            continue

        hash_count = 0
        while lines[i][hash_count] == '#':
            hash_count += 1

        if hide_toc and within_toc:
            if hash_count != 0:
                within_toc = False
            else:
                lines[i]= ""
                continue

        if hash_count == 0 or hash_count > 6:
            continue

        # Node names must not use periods, commas, or colons, or start with a left parenthesis.
        name = lines[i][hash_count:]
        name = name.replace(".", " ")
        name = name.replace(",", " ")
        name = name.replace(":", " ")
        if name.startswith('('):
            name[0] = ' '

        if hash_count > prev_hash_count:
            nest_level = min(nest_level + 1, 4)
        elif hash_count < prev_hash_count:
            nest_level = max(nest_level - (prev_hash_count - hash_count), 1)

        prev_hash_count = hash_count

        # Always specify a new node for each chapter,
        # but do not for any other section if inline is specified.
        if nest_level == 1 or not inline:
            lines[i] = "@node" + name + '\n'
        else:
            lines[i] = ""

        if nest_level == 1:
            lines[i] += "@chapter" + name
        elif nest_level == 2:
            lines[i] += "@section" + name
        elif nest_level == 3:
            lines[i] += "@subsection" + name
        elif nest_level == 4:
            lines[i] += "@subsubsection" + name
        else:
            print("ERROR: Invalid nest level")

    return ('\n'.join(lines), title)

    
def parse_headers(src, inline):
    lines = src.split('\n')
    for i in range(len(lines)):
        if len(lines[i]) < 2:
            continue

        count = 0
        while (lines[i][count] == '#'):
            count += 1

        if count == 0:
            continue

        if count > 4:
            lines[i] = lines[i][count+1:]
            continue
        
        name = lines[i][count:]

        # Always specify a new node for each chapter,
        # but do not for any other section if inline is specified.
        if count == 1 or not inline:
            lines[i] = "@node" + name + '\n'
        else:
            lines[i] = ""

        if count == 1:
            lines[i] += "@chapter" + name
        elif count == 2:
            lines[i] += "@section" + name
        elif count == 3:
            lines[i] += "@subsection" + name
        elif count == 4:
            lines[i] += "@subsubsection" + name

    return '\n'.join(lines)


names_used = set()
def parse_anchors(src):
    lines = src.split('\n')
    for i in range(len(lines)):
        # Minimum length: "<a></a>"
        if len(lines[i]) < 7:
            continue

        anchors = finditer(r'<a[^/].*>.*</a>', lines[i])
        for anchor in anchors:
            name = search(r'(name=")(.*)(")', anchor.group())
            if name.groups()[1]:
                lines[i] = lines[i].replace(anchor.group(), "")
                if name.groups()[1] not in names_used:
                    lines[i] += "\n@anchor{" + name.groups()[1] + "}\n"
                    names_used.add(name.groups()[1])

                  
    return '\n'.join(lines)


def is_bulleted_list_line(line):
    return line.startswith("- ") \
        or line.startswith("+ ") \
        or line.startswith("* ")


def parse_bulleted_lists(src):
    lines = src.split('\n')
    is_list = False
    for i in range(len(lines)):
        if len(lines[i]) < 2:
            if is_list:
                lines[i] = "@end itemize\n" + lines[i]
                is_list = False
            continue

        # Detect all of the entries within a list.
        if is_list:
            if is_bulleted_list_line(lines[i]):
                lines[i] = "@item\n" + lines[i][2:]
            else:
                lines[i] = "@end itemize\n" + lines[i]
                is_list = False
            continue

        # Detect the start of a list.
        if is_bulleted_list_line(lines[i]):
            lines[i] = "@itemize\n@item\n" + lines[i][2:]
            is_list = True

    return '\n'.join(lines)


# FIXME: Checking exact indices for specific characters
#        is quite possibly the worst way to do this.
def parse_enumerated_lists(src):
    lines = src.split('\n')
    is_list = False
    for i in range(len(lines)):
        # Minimum length: "1. a"
        if len(lines[i]) < 4:
            if is_list:
                lines[i] = "@end enumerate\n" + lines[i]
                is_list = False
            continue

        # Detect all of the entries within a list.
        if is_list:
            if lines[i][0].isdigit() and lines[i][1] == '.' and lines[i][2] == ' ':
                lines[i] = "@item\n" + lines[i][3:]
            else:
                lines[i] = "@end enumerate\n" + lines[i]
                is_list = False
            continue

        # Detect the start of a list.
        if lines[i][0].isdigit() and lines[i][1] == '.' and lines[i][2] == ' ':
            lines[i] = "@enumerate\n@item\n" + lines[i][3:]
            is_list = True

    return '\n'.join(lines)


# TODO: Parse nested lists!
def parse_lists(src):
    out = src
    out = parse_bulleted_lists(out)
    out = parse_enumerated_lists(out)
    return out


def parse_code(src):
    lines = src.split('\n')
    in_block = False
    for i in range(len(lines)):
        # Minimum length: "` `"
        if len(lines[i]) < 3:
            continue

        # Triple backtick code blocks
        if lines[i].startswith("```"):
            if in_block:
                lines[i] = "@end example"
                in_block = False
            else:
                lines[i] = "@example"
                in_block = True
            continue


        # Single backtick wrapped code segments
        code_in_quotes = finditer(r'`.+?`', lines[i])
        for code in code_in_quotes:
            lines[i] = lines[i].replace(code.group(), "@code{" + code.group()[1:-1] + "}")

    return '\n'.join(lines)


def parse_images(src):
    lines = src.split('\n')
    for i in range(len(lines)):
        # Minimum length: "![a](b)"
        if len(lines[i]) < 7:
            continue

        images = finditer(r'!\[(.*?)\] *\((.*?)\)', lines[i])
        for image in images:
            alt_text, link = image.groups()
            # FIXME: Not all image links end with an extension!
            filename, extension = link.rsplit('.', 1)
            lines[i] = lines[i].replace(image.group(), "@image{" + filename + ",,," + alt_text + "," + extension + "}")

    return '\n'.join(lines)


# NOTE: This function gets confused at images,
#       so be sure to parse_images() first!
def parse_links(src):
    lines = src.split('\n')
    for i in range(len(lines)):
        # Minimum length: "[a](b)"
        if len(lines[i]) < 6:
            continue

        links = finditer(r'\[(.+?)\] *\((.+?)\)', lines[i])
        for it in links:
            name, link = it.groups()
            if link.startswith('#'):
                replacement = "@ref{" + link[1:]
                if name:
                    replacement += ",," + name
                replacement += "}"
                lines[i] = lines[i].replace(it.group(), replacement)
                continue

            replacement = "@url{" + link
            if name:
                replacement += ", " + name

            replacement += "}"
            lines[i] = lines[i].replace(it.group(), replacement)

    return '\n'.join(lines)


def parse_bold(src):
    lines = src.split('\n')
    for i in range(len(lines)):
        # Minimum length: "**a**"
        if len(lines[i]) < 5:
            continue

        bold_text = finditer(r'([\*\_])\1(.*)([\*\_])\1', lines[i])
        for it in bold_text:
            lines[i] = lines[i].replace(it.group(), "@strong{" + it.group()[2:-2] + "}")

    return '\n'.join(lines)


def parse_italics(src):
    lines = src.split('\n')
    for i in range(len(lines)):
        # Minimum length: "*a*"
        if len(lines[i]) < 3:
            continue

        italic_text = finditer(r'\*.*\*', lines[i])
        for it in italic_text:
            lines[i] = lines[i].replace(it.group(), "@emph{" + it.group()[1:-1] + "}")

    return '\n'.join(lines)


def parse_at_characters(src):
    lines = src.split('\n')
    links = "\\[(.+?)\\] *\\((.+?)\\)"
    code_single = "`.+?`"

    for i in range(len(lines)):
        unescaped_at_characters = finditer(r'@', lines[i])
        for it in unescaped_at_characters:
            lines[i] = lines[i].replace(it.group(), '@' + it.group())

    return '\n'.join(lines)

def parse_escaped_characters(src):
    lines = src.split('\n')
    links = "\\[(.+?)\\] *\\((.+?)\\)"
    code_single = "`.+?`"

    for i in range(len(lines)):
        # Minimum length: "\a"
        if len(lines[i]) < 2:
            continue
        
        # TODO: Figure out how to skip triple backtick code blocks...
        verbatim_texts = finditer(r'' + links
                                  + '|' + code_single
                                  , lines[i])

        # Parse markdown escaped characters
        escaped_characters = finditer(r'\\.', lines[i])
        for it in escaped_characters:
            skip = False
            for txt in verbatim_texts:
                if it.group() in txt.group():
                    skip = True
                    break

            if skip:
                skip = False
                continue

            character = it.group()[1]
            # The following characters must be escaped in markdown but not Texinfo
            if character == '\\'   \
               or character == '`' \
               or character == '*' \
               or character == '_' \
               or character == '[' \
               or character == ']' \
               or character == '<' \
               or character == '>' \
               or character == '(' \
               or character == ')' \
               or character == '#' \
               or character == '+' \
               or character == '-' \
               or character == '.' \
               or character == '!' \
               or character == '|':
                lines[i] = lines[i].replace(it.group(), character)

            # The following characters must be escaped in Texinfo as well as markdown
            if character == '{' \
               or character == '}':
                lines[i] = lines[i].replace(it.group(), '@' + character)

    return '\n'.join(lines)


def parse_trailing_backslash(src):
    lines = src.split('\n')
    for i in range(len(lines)):
        # Minimum length: " \"
        if len(lines[i]) < 2:
            continue

        if lines[i].endswith(" \\"):
            lines[i] = lines[i][:-2] + '\n\n'
        
    return '\n'.join(lines)


def parse_html_comments(src):
    lines = src.split('\n')
    for i in range(len(lines)):
        # Minimum length: "<!---->"
        if len(lines[i]) < 7:
            continue

        comments_in_line = finditer(r'<!--.*-->', lines[i])
        for comment in comments_in_line:
            lines[i] = lines[i].replace(comment.group(), "")
        
    return '\n'.join(lines)


def parse_markdown(src, title, inline, hide_toc):
    out = src
    out = parse_at_characters(out)
    out = parse_trailing_backslash(out)
    out = parse_html_comments(out)
    out = parse_anchors(out)
    out, title = parse_headers_new(out, title, inline, hide_toc)
    out = parse_lists(out)
    out = parse_escaped_characters(out)
    out = parse_bold(out)
    out = parse_italics(out)
    out = parse_code(out)
    out = parse_images(out)
    out = parse_links(out)
    return (out, title)


# Returns a tuple with information parsed from command line arguments with the following structure:
#     (
#          file_path
#          , output_file_path
#          , title_of_manual
#          , should_inline_sections
#          , hide_table_of_contents
#      )
def parse_cmd_args():
    argc = len(argv)
    if argc < 2:
        print_usage()

    file_path = ""
    title = ""
    output_file_path = ""
    inline = False
    hide_toc = False

    i = 1
    while i < argc:
        arg = argv[i]
        if "-h" in arg.lower() and "--h" not in arg.lower():
            print_usage()
        elif arg.startswith("-t"):
            if i + 1 >= argc:
                print("ERROR: Expected a title to be specified after `-t` option.")
                exit(1)
            i += 1
            title = argv[i]
        elif arg.startswith("-o"):
            if i + 1 >= argc:
                print("ERROR: Expected an output file path to be specified after `-o` option.")
                exit(1)
            i += 1
            output_file_path = argv[i]
        elif arg.startswith("-i") or arg.startswith("--inline"):
            inline = True
        elif arg.startswith("--hide-toc"):
            hide_toc = True
        else:
            if not file_path:
                file_path = arg
            else:
                print("ERROR: Multiple file paths specified (command line argument unrecognized)")
                exit(1)

        i += 1

    if not file_path:
        print("ERROR: No file path was given, or was not able to be parsed from the command line arguments given.")
        exit(1)

    if not file_path.lower().endswith(".md"):
        print("ERROR: The file path given is not a valid markdown file (wrong extension).")
        print(" -> ", file_path)
        exit(1)    



    return (file_path, output_file_path, title, inline, hide_toc)


def main():
    file_path, output_file_path, title, inline, hide_toc = parse_cmd_args()
    with open(file_path) as markdown:
        md = markdown.read()
        md, title = parse_markdown(md, title, inline, hide_toc)

        # If no manual title is specified on the command
        # line, generate one from the input file name.
        if not title:
            title = path.basename(file_path)

        # If no output file path is specified on the command
        # line, generate one from the title.
        # Convert to lowercase and replace all spaces with
        # underscores to ensure valid file name.
        if not output_file_path:
            output_file_path = title.lstrip().lower().replace(' ', '_') + ".texi"

        with open("template.texi") as template:
            texi = template.read()
            texi = texi.replace("$${{TITLE}}$$", title)
            texi = texi.replace("$${{CONTENTS}}$$", md)
            with open(output_file_path, 'w') as out:
                out.write(texi)


if __name__ == "__main__":
    main()
