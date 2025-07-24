# Set the default PDF viewer
$pdf_mode = 1;  # 1 for PDF mode

$bibtex_use = 2;

# Specify the main file to be processed
$main_file = 'main.tex';  # Change this to your main LaTeX file

# Automatically clean auxiliary files on successful build
$clean_ext = 'aux,log,out,blg,bbl,toc,dvi';

# Set the default compiler
$latex = 'pdflatex %O %S';

# Options for bibtex
$biblio = 'bibtex %B';

# Enable continuous mode, if desired
$continuous_mode = 1;

# Add your own custom rules or configurations below
$pdflatex = 'pdflatex -synctex=1 --interaction=nonstopmode -file-line-error';

# Use BibTeX for bibliography processing
$bibtex = 'bibtex';

# Ensure proper processing with BibTeX
$cleanup = 'aux bbl bcf blg';

