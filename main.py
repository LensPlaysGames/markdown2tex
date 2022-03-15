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
    print("    -o <path>      -- Specify the filepath where the Texinfo manual will be saved to")
    print()
    exit(0)

    
def parse_headers(src, inline):
    lines = src.split('\n')
    for i in range(len(lines)):
        line = lines[i]
        if len(line) < 2:
            continue

        count = 0
        while (line[count] == '#'):
            count += 1

        if count == 0:
            continue

        if count > 4:
            lines[i] = line[count+1:]
            continue
        
        name = line[count:]

        # Always specify a new node for each chapter,
        # but do not for any other section if inline is specified.
        if count == 1 or not inline:
            line = "@node" + name + '\n'
        else:
            line = ""

        if count == 1:
            line += "@chapter" + name
        elif count == 2:
            line += "@section" + name
        elif count == 3:
            line += "@subsection" + name
        elif count == 4:
            line += "@subsubsection" + name

        lines[i] = line

    return '\n'.join(lines)


def parse_bulleted_lists(src):
    lines = src.split('\n')
    is_list = False
    for i in range(len(lines)):
        line = lines[i]
        if len(line) < 2:
            if is_list:
                lines[i] = "@end itemize\n" + line
                is_list = False
            continue

        # Detect all of the entries within a list.
        if is_list:
            if line.startswith("- "):
                line = "@item\n" + line[2:]
            else:
                line = "@end itemize\n" + line
                is_list = False

            lines[i] = line
            continue

        # Detect the start of a list.
        if line.startswith("- "):
            line = "@itemize\n@item\n" + line[2:]
            is_list = True
            
        lines[i] = line

    return '\n'.join(lines)


# FIXME: Checking exact indices for specific characters
#        is quite possibly the worst way to do this.
def parse_enumerated_lists(src):
    lines = src.split('\n')
    is_list = False
    for i in range(len(lines)):
        line = lines[i]
        # Minimum length: "1. a"
        if len(line) < 4:
            if is_list:
                lines[i] = "@end enumerate\n" + line
                is_list = False
            continue

        # Detect all of the entries within a list.
        if is_list:
            if line[0].isdigit() and line[1] == '.' and line[2] == ' ':
                line = "@item\n" + line[3:]
            else:
                line = "@end enumerate\n" + line
                is_list = False

            lines[i] = line
            continue

        # Detect the start of a list.
        if line[0].isdigit() and line[1] == '.' and line[2] == ' ':
            line = "@enumerate\n@item\n" + line[3:]
            is_list = True
            
        lines[i] = line

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
        line = lines[i]
        # Minimum length: "` `"
        if len(line) < 3:
            continue

        code_in_quotes = finditer(r'`.+?`', line)
        for code in code_in_quotes:
            line = line.replace(code.group(), "@code{" + code.group()[1:-1] + "}")

        lines[i] = line

    return '\n'.join(lines)


def parse_images(src):
    lines = src.split('\n')
    is_list = False
    for i in range(len(lines)):
        line = lines[i]
        # Minimum length: "![a](b)"
        if len(line) < 7:
            continue

        images = finditer(r'!\[(.*?)\] *\((.*?)\)', line)
        for image in images:
            alt_text, link = image.groups()
            filename, extension = link.rsplit('.', 1)
            line = line.replace(image.group(), "@image{" + filename + ",,," + alt_text + ",." + extension + "}")

        lines[i] = line

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

    filepath = ""
    title = ""
    output_filepath = ""
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
                print("ERROR: Expected an output filepath to be specified after `-o` option.")
                exit(1)
            i += 1
            output_filepath = argv[i]
        elif arg.startswith("-i") or arg.startswith("--inline"):
            inline = True
        else:
            if not filepath:
                filepath = arg
            else:
                print("ERROR: Multiple filepaths specified (command line argument unrecognized)")
                exit(1)

        i += 1

    if not filepath:
        print("ERROR: No filepath was given, or was not able to be parsed from the command line arguments given.")
        exit(1)

    if not filepath.lower().endswith(".md"):
        print("ERROR: The path given is not a valid markdown file (wrong extension).")
        print(" -> ", filepath)
        exit(1)

    if not title:
        title = path.basename(filepath)

    if not output_filepath:
        output_filepath = title.lstrip().lower().replace(' ', '_') + ".tex"
    
    with open(filepath) as markdown:
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
            with open(output_filepath, 'w') as out:
                out.write(tex)


if __name__ == "__main__":
    main()
