This python script converts a markdown file given on the command line into a TeX file utilizing the GNU Texinfo set of macros.

NOTE: This is a work in progress; feel free to submit any pull requests of any changes that you have implemented. [Github Repository](https://www.github.com/user/LensPlaysGames/markdown2tex)

# Dependencies
All of the dependencies for this program are free software (open source).

- [Python](https://www.python.org/)
- [GNU Texinfo](https://www.gnu.org/software/texinfo/)

NOTE: On Windows, depending on what version of GNU Texinfo you have, you may get lots of errors and it may not work when trying to run `makeinfo`. I recommend WSL. No problems. The script generates everything correctly, but the Windows version of `makeinfo` isn't always robust.

# Conversion

## What is a Valid Markdown File to this Parser?
A `#` at the beginning of a line indicates that a new chapter is started.

Any subsequent `##` will be sections of the most recently decalred chapter.

Any subsequent `###` will be subsections of the most recently declared section. 

Any subsequent `####` will be subsubsections of the most recently declared subsection.

If, for example, a subsubsection is declared without a parent subsection, GNU Texinfo will give a warning about having to "raise" it up, but in the end everything will still work.

If the chapter/section/subsection/subsubsection structure is confusing, look into the `info` pages of `info` itself, or even `texinfo`.

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
