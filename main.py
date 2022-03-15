from os import path
from re import finditer, search
from sys import argv

# TODO:
# |-- Ignore single end of line, as markdown does
# |-- Parse markdown tables into GNU Texinfo multitables
# `-- Implement '\' end of line (hide in TeX output)

def print_usage():
    print("Markdown to GNU Texinfo Converter by Rylan `Lens` Kellogg")
    print()
    print("Usage:")
    print("    python main.py [FLAGS] [OPTIONS] \"path/to/markdown.md\"")
    print()
    print("Flags:")
    print("    -h, --help     -- Show the help dialog in stdout")
    print("    -i, --inline   -- Do not specify new nodes for sections within chapters.")
    print()
    print("Options:")
    print("    -t <title>     -- Specify the title of the Texinfo manual that is generated")
    print("    -o <path>      -- Specify the file path where the Texinfo manual will be saved to")
    print()
    exit(0)

    
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
            if lines[i].startswith("- ") or lines[i].startswith("* "):
                lines[i] = "@item\n" + lines[i][2:]
            else:
                lines[i] = "@end itemize\n" + lines[i]
                is_list = False
            continue

        # Detect the start of a list.
        if lines[i].startswith("- "):
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
    is_list = False
    for i in range(len(lines)):
        # Minimum length: "` `"
        if len(lines[i]) < 3:
            continue

        code_in_quotes = finditer(r'`.+?`', lines[i])
        for code in code_in_quotes:
            lines[i] = lines[i].replace(code.group(), "@code{" + code.group()[1:-1] + "}")

    return '\n'.join(lines)


def parse_images(src):
    lines = src.split('\n')
    is_list = False
    for i in range(len(lines)):
        # Minimum length: "![a](b)"
        if len(lines[i]) < 7:
            continue

        images = finditer(r'!\[(.*?)\] *\((.*?)\)', lines[i])
        for image in images:
            alt_text, link = image.groups()
            filename, extension = link.rsplit('.', 1)
            lines[i] = lines[i].replace(image.group(), "@image{" + filename + ",,," + alt_text + ",." + extension + "}")

    return '\n'.join(lines)


# NOTE: This function gets confused at images,
#       so be sure to parse_images() first!
def parse_links(src):
    lines = src.split('\n')
    is_list = False
    for i in range(len(lines)):
        # Minimum length: "[a](b)"
        if len(lines[i]) < 6:
            continue

        links = finditer(r'\[(.+?)\] *\((.+?)\)', lines[i])
        for it in links:
            name, link = it.groups()
            if link.startswith('#'):
                print("WARNING: markdown2tex does not yet support links to anchors")
                continue

            replacement = "@url{" + link
            if name:
                replacement += ", " + name

            replacement += "}"
            lines[i] = lines[i].replace(it.group(), replacement)

    return '\n'.join(lines)


def main():
    argc = len(argv)
    if argc < 2:
        print_usage()

    file_path = ""
    title = ""
    output_file_path = ""
    inline = False

    i = 1
    while i < argc:
        arg = argv[i]
        if "-h" in arg.lower():
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

    if not title:
        title = path.basename(file_path)

    # If no output file path is specified on the command line, generate one from the title.
    # Convert to lowercase and replace all spaces with underscores to ensure valid file name.
    if not output_file_path:
        output_file_path = title.lstrip().lower().replace(' ', '_') + ".tex"
    
    with open(file_path) as markdown:
        with open("template.tex") as template:
            md = markdown.read()
            md = parse_headers(md, inline)
            md = parse_lists(md)
            md = parse_code(md)
            md = parse_images(md)
            md = parse_links(md)
            tex = template.read()
            tex = tex.replace("$${{TITLE}}$$", title)
            tex = tex.replace("$${{CONTENTS}}$$", md)
            with open(output_file_path, 'w') as out:
                out.write(tex)


if __name__ == "__main__":
    main()
