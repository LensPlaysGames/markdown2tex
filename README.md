This python script converts a markdown file given on the command line into a TeX file utilizing the GNU Texinfo set of macros. GNU Texinfo can then convert that source file into HTML, PDF, XML, and more formats.

NOTE: This is a work in progress; feel free to submit any pull requests of any changes that you have implemented. [Github Repository](https://www.github.com/LensPlaysGames/markdown2tex)

## Dependencies
All of the dependencies for this program are free software (open source).

- [Python](https://www.python.org/)
- [GNU Texinfo](https://www.gnu.org/software/texinfo/)

NOTE: On Windows, depending on what version of GNU Texinfo you have, you may get lots of errors and it may not work when trying to run `makeinfo`. I recommend WSL. No problems. The script generates everything correctly, but the Windows version of `makeinfo` isn't always robust.

## Conversion

### What is a Valid Markdown File to this Parser?
Technically, all files containing only valid markdown are valid to this parser, but not all features of all markdown syntaxes are supported, and some layouts may not make any sense in the final output.

For a full outline of how the layout of the generated Texinfo source file is determined [the # Headers Section](#hash-headers).

### Converting This File into an Info Page
We will first convert this README markdown file into a Texinfo source file. 

We can then use Texinfo to convert that source file into an info file that can be viewed with the `info` command.

In a terminal that is open on a machine with the required dependencies installed, invoke the following commands:

`cd /path/to/markdown2tex/`

`python main.py -t "Markdown2Tex Converter" README.md`

`makeinfo markdown2tex_converter.tex`

Everything is all generated at this point! Take a look using `info`:

`info -f markdown2tex_converter.info`

Many formats are supported by `makeinfo`, and can be found by invoking the command with the `-h` command line flag.

### Command Line Flags and Options
To get help with the options and flags that may be specified, use the following command:

`python /path/to/markdown2tex/main.py -h`

This will print out the layout of the command (usage), as well as the flags and options available and a short description of what they do to the standard output.

## Capabilities
In no particular order, here is an incomprehensive exploration of markdown features that are currently supported by 
markdown2tex.

### `#` Headers <a name="hash-headers"></a>
Headers are parsed according to the following rules:
- If no line that starts with leading `#` characters has been found, the first occurence of one such line will set `hash_count` to the amount of hashes present and `nest_level` to `1`, indicating a chapter.
- If any subsequent line starts with an amount of leading `#` characters that is greater than `hash_count` (the previous header line's amount of leading `#` characters), `nest_level` is increased by `1`, up to a max of `4`. `hash_count` is updated.
- If any subsequent line starts with an amount of leading `#` characters that is less than `hash_count`, `nest_level` is reduced by the difference in current `hash_count` and previous `hash_count`. `hash_count` is updated.
- If any subsequent line starts with an amount of leading `#` characters that is equal to `hash_count`, `nest_level` stays the same.

Meaning of `nest_level`:
- 1 -> Chapter
- 2 -> Section
- 3 -> Subsection
- 4 -> Subsubsection

If you use the lines that start with `#` in markdown as anything other than a label for the following chunk of text, you will likely have errors in the generated output structure. Other than that, this parse makes little other assumptions about the input markdown.

### Text

#### Emphasizing Text
Text may be differentiated from the text around it by emphasizing it (usually italicized in final output). To emphasize text in markdown, wrap it in the '\*' character.

*I've been emphasized :^)*

Important text may be emboldened, or strengthened, by wrapping it in two '\*' characters.

**I am emboldened!**

Code may be represented in a monospace font by wrapping it in the '\`' backtick character.

`This is an example of a simple code block`

#### Escaping Characters
Some characters are escapable in markdown, and that holds true for this converter as well.

\\ Backslash

\` Backtick

\* Asterisk

\_ Underscore

\{ Open Brace

\} Close Brace

\[ Open Bracket

\] Close Bracket

\< Open Angle Bracket

\> Close Angle Bracket

\( Open Parenthesis

\) Close Parenthesis

\# Hash (Pound)

\+ Plus

\- Minus (En-dash)

\. Period (Dot)

\! Exclamation Point

\| Pipe


### Lists
Nested lists are not yet supported, however regular old lists and numbered lists (enumerations) are supported.

For example, here's a list of the lists currently supported:
- Bulleted Lists
- Numbered Lists

For an example of a numbered list, here are the steps to get back to the "Capabilities" chapter.
1. Press the `u` button on the keyboard
2. ???
3. Profit!

### Cross-References

#### Anchors
By inserting an HTML anchor with a name attribute, and linking to it with a markdown-style link syntax, this parser will generate both the anchor and the reference link for Texinfo. This means it will be a valid cross-reference online (via a hyperlink), offline (via an explicitly printed URL), or printed out on paper (with page numbers and everything). 

To correctly link to an anchor on the same page, use a `#` prefix on the value of the name attribute, as is standard in markdown.

[Here is a link to the next section](#referencing-urls), all about referencing URLs

#### URLs <a name="referencing-urls"></a>
The following is a link to the Github Repository of this program.

Visit there and click that star button, if you wish :^)

[Github Repository](https://www.github.com/LensPlaysGames/markdown2tex)

#### Images
The following is an image; on some representations, you'll only see the alternative text, while on others, you will see the image instead.

![A small icon of the letter M](M.png)