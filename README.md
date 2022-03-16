This python script converts a markdown file given on the command line into a TeX file utilizing the GNU Texinfo set of macros. GNU Texinfo can then convert that source file into HTML, PDF, XML, and more formats.

NOTE: This is a work in progress; feel free to submit any pull requests of any changes that you have implemented. [Github Repository](https://www.github.com/LensPlaysGames/markdown2tex)

# Dependencies
All of the dependencies for this program are free software (open source).

- [Python](https://www.python.org/)
- [GNU Texinfo](https://www.gnu.org/software/texinfo/)

NOTE: On Windows, depending on what version of GNU Texinfo you have, you may get lots of errors and it may not work when trying to run `makeinfo`. I recommend WSL. No problems. The script generates everything correctly, but the Windows version of `makeinfo` isn't always robust.

# Conversion

## What is a Valid Markdown File to this Parser?
For a (more) comprehensive outline of the markdown features supported by this converter, see the "Capabilities" chapter.

A `#` at the beginning of a line indicates that a new chapter is started.

Any subsequent `##` will be sections of the most recently decalred chapter.

Any subsequent `###` will be subsections of the most recently declared section. 

Any subsequent `####` will be subsubsections of the most recently declared subsection.

If, for example, a subsubsection is declared without a parent subsection, GNU Texinfo will give a warning about having to "raise" it up, but in the end everything will still work.

If the chapter/section/subsection/subsubsection structure is confusing, look into the `info` pages of `texinfo`, or even `info` itself.

This document is also an example of what this parser can understand, and will be what we will be converting as our example in the next section.

## Converting This File into an Info Page
We will first convert this README markdown file into a Texinfo source file. 

We can then use Texinfo to convert that source file into an info file that can be viewed with the `info` command.

In a terminal that is open on a machine with the required dependencies installed, invoke the following commands:

`cd /path/to/markdown2tex/`

`python main.py -t "Markdown2Tex Converter" README.md`

`makeinfo markdown2tex_converter.tex`

Everything is all generated at this point! Take a look using `info`:

`info -f markdown2tex_converter.info`

## Command Line Flags and Options
To get help with the options and flags that may be specified, use the following command:

`python /path/to/markdown2tex/main.py -h`

This will print out the layout of the command (usage), as well as the flags and options available and a short description of what they do to the standard output.

# Capabilities
In no particular order, here is an incomprehensive exploration of markdown features that are currently supported by 
markdown2tex.

## `#` Headers
One or up to four `#` character(s) at the beginning of a line will create a new chapter, section, subsection, and subsubsection in GNU Texinfo format.

## Text

### Emphasizing Text
Text may be differentiated from the text around it by emphasizing it (usually italicized in final output). To emphasize text in markdown, wrap it in the '\*' character.

*I've been emphasized :^)*

Important text may be emboldened, or strengthened, by wrapping it in two '\*' characters.

**I am emboldened!**

Code may be represented in a monospace font by wrapping it in the '\`' backtick character.

`This is an example of a simple code block`

### Escaping Characters
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


## Lists
Nested lists are not yet supported, however regular old lists and numbered lists (enumerations) are supported.

For example, here's a list of the lists currently supported:
- Bulleted Lists
- Numbered Lists

For an example of a numbered list, here are the steps to get back to the "Capabilities" chapter.
1. Press the `u` button on the keyboard
2. ???
3. Profit!

## Cross-References

### URLs
The following is a link to the Github Repository of this program.

Visit there and click that star button, if you wish :^)

[Github Repository](https://www.github.com/LensPlaysGames/markdown2tex)

### Images
The following is an image; on some representations, you'll only see the alternative text, while on others, you will see the image instead.

![A small icon of the letter M](M.png)