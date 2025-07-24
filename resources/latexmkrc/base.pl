# Output directory for PDF and other build artifacts.
$out_dir = 'target';

# Output directory for auxiliary files.
$aux_dir = 'target';

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
# $pdf_previewer = "open";
# $pdf_previewer = 'start evince';

# Whether to automatically rerun if necessary.
$preview_continuous_mode = 1;

# Whether to silence logfile warnings.
$silence_logfile_warnings = 1;

# TEXINPUTS (List of directories to look for TeX files).
my $texinputs_prior = $ENV{'TEXINPUTS'} // '';
my @my_texinputs = ();
# Preserves existing directories.
push @my_texinputs, $texinputs_prior if $texinputs_prior ne '';
# Includes current directory.
push @my_texinputs, '.';
# Includes src directory recursively (double slash!).
push @my_texinputs, 'src//';
$ENV{'TEXINPUTS'} = join(':', @my_texinputs);

# List of file extensions to be cleaned up.
my @my_clean_ext = (
    'acn',
    'acr',
    'alg',
    'aux',
    'bbl',
    'blg',
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
    'out',
    'toc',
    'xdy',
    'fdb_latexmk',
    'fls',
    'nav',
    'snm',
    'synctex.gz',
    'vrb',
);
$clean_ext = join(' ', @my_clean_ext);

# List of generated extensions to add.
my @more_generated_exts = (
    'glg',
    'glo',
    'gls',
    'acn',
    'acr',
    'alg',
    'bbl',
    'blg',
);
push @generated_exts, @more_generated_exts;
