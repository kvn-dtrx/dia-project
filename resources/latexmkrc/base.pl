# ---
# begin: .latexmkrc <- dia-project
# ---

# ---

# Output directory for PDF and other build artifacts.
$out_dir = 'build';

# Output directory for auxiliary files.
$aux_dir = 'build';

# LaTeX engine: 1 = pdflatex, 4 = lualatex, 5 = xelatex
$pdf_mode = 1;

# Bibliography mode: # 0=off, 1=bibtex, 2=auto-detect (bibtex/biber).
$bibtex_use = 2;

# Command to run when compilation fails.
$failure_cmd = 'echo "** Compilation failed **"';

# Whether to enable preview mode.
$preview_mode = 0;

# Whether to enable continuous preview (with -pvc).
$pvc_view_file_via_temporary = 0;

# Custom viewer (optional)
$pdf_previewer = "open";
# $pdf_previewer = 'start evince';

# Whether to automatically rerun if necessary.
$preview_continuous_mode = 0;

# Whether to silence logfile warnings.
$silence_logfile_warnings = 1;

# TEXINPUTS (List of directories to look for TeX files).
$ENV{'TEXINPUTS'} = join(':', (
    # Includes current directory.
    '.',
    # Includes src directory recursively (double slash!).
    'src//', 
    # Includes src directory recursively (double slash!).
    'styles//',
    # Preserves existing directories.
    $ENV{'TEXINPUTS'} // '',
));

# BIBINPUTS (List of directories to look for BibTeX files).
$ENV{'BIBINPUTS'} = join(':', (
    # Includes styles directory recursively (double slash!).
    'bib//', 
    # Preserves existing directories.
    $ENV{'BIBINPUTS'} // '',
));

# List of file extensions to be cleaned up.
my @my_clean_ext = (
    'acn',
    'acr',
    'alg',
    'aux',
    'bbl',
    'blg',
    'fdb_latexmk',
    'fls',
    'glg',
    'glo',
    'gls',
    'idx',
    'ilg',
    'ind',
    'ist',
    'lof',
    'log',
    'lol',
    'lot',
    'maf',
    'mtc',
    'mtc0',
    'nav',
    'out',
    'snm',
    'synctex.gz',
    'tmp',
    'thm',
    'toc',
    'vrb',
    'xdy',
);
$clean_ext = join(' ', @my_clean_ext);

# List of generated extensions to add.
my @more_generated_exts = (
    'acn',
    'acr',
    'alg',
    'bbl',
    'blg',
    'glg',
    'glo',
    'gls',
);
push @generated_exts, @more_generated_exts;

# ---

# ---
# end: .latexmkrc <- dia-project
# ---
