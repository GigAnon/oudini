#! python3
import copy
import  shutil
import  subprocess
import  envutils

from    compiler        import Compiler
from    document        import Document

from    pathlib         import Path
from    typing          import Optional
from    typing          import Union


class MiktexCompiler (Compiler):
    """
        LaTeX compiler class for MikTex distribution (pdflatex + makeglossaries-lite)
    """
    DEFAULT_PDFLATEX_BIN   = "pdflatex"
    DEFAULT_GLOSSARIES_BIN = "makeglossaries-lite"

    def __init__(self,
                 i_miktex_bin_dir : Optional[Union[str,
                                                   Path]] = None,
                 i_pdflatex_bin   : [str] = DEFAULT_PDFLATEX_BIN,
                 i_glossaries_bin : [str] = DEFAULT_GLOSSARIES_BIN):
        assert isinstance(i_miktex_bin_dir, str)    or \
               isinstance(i_miktex_bin_dir, Path)   or \
               i_miktex_bin_dir is None
        assert isinstance(i_pdflatex_bin,   str)
        assert isinstance(i_glossaries_bin, str)

        super().__init__()

        self.pdflatex_bin   = i_pdflatex_bin
        self.glossaries_bin = i_glossaries_bin

        if i_miktex_bin_dir:
            self.miktex_bin_dir = Path(i_miktex_bin_dir)
        else:
            self.miktex_bin_dir = None

        # Build execution environments for pdflatex and makeglossaries-lite
        envar_path = envutils.EnvarPath.from_environ()

        if self.miktex_bin_dir:
            envar_path.append(self.miktex_bin_dir.resolve())

        self.pdflatex_env   = envutils.Env(PATH = str(envar_path))
        self.glossaries_env = envutils.Env(PATH = str(envar_path))


    def run(self,
            i_doc_root_dir: Union[str, Path],
            i_output_dir  : Union[str, Path],
            i_document    : Optional[Document] = None) -> None:
        assert isinstance(i_document, Document) or i_document is None
        assert isinstance(i_doc_root_dir, str) or \
               isinstance(i_doc_root_dir, Path)
        assert isinstance(i_output_dir, str) or \
               isinstance(i_output_dir, Path)

        if isinstance(i_output_dir, str):
            i_output_dir = Path(i_output_dir)

        # TODO better system
        LATEX_MAIN_DOC_NAME = "main"
        output_filename     = "%s.pdf" % (LATEX_MAIN_DOC_NAME)
        output_file         = i_output_dir.joinpath(output_filename)

        output_tmp_dir      = i_output_dir.joinpath('tmp')
        output_tmp_file     = output_tmp_dir.joinpath(output_filename)

        # TODO use logging system
        print("Removing '%s'" % (output_tmp_dir))
        shutil.rmtree(path          = output_tmp_dir,
                      ignore_errors = True)

        print("Removing '%s'" % (output_filename))
        try:
            output_file.unlink(missing_ok = True)
        except PermissionError:
            print("Warning: could not delete '%s'" % (output_file))
            pass

        print("Running %s (1)" % (self.pdflatex_bin))
        self._invoke_pdflatex(i_latex_folder = i_doc_root_dir,
                              i_temp_folder  = output_tmp_dir,
                              i_docname      = LATEX_MAIN_DOC_NAME)

        print("Running %s (1)" % (self.glossaries_bin))
        self._invoke_makeglossaries(i_temp_folder  = output_tmp_dir,
                                    i_docname      = LATEX_MAIN_DOC_NAME)

        print("Running %s (2)" % (self.pdflatex_bin))
        self._invoke_pdflatex(i_latex_folder = i_doc_root_dir,
                              i_temp_folder  = output_tmp_dir,
                              i_docname      = LATEX_MAIN_DOC_NAME)

        print("Running %s (3)" % (self.pdflatex_bin))
        self._invoke_pdflatex(i_latex_folder = i_doc_root_dir,
                              i_temp_folder  = output_tmp_dir,
                              i_docname      = LATEX_MAIN_DOC_NAME)

        print("Copying '%s' to '%s'" % (output_tmp_file, output_file))
        shutil.copy(output_tmp_file, output_file)


    def _invoke_pdflatex(self,
                         i_latex_folder : Path,
                         i_temp_folder  : Path,
                         i_docname      : str):
        assert isinstance(i_temp_folder, Path)
        assert isinstance(i_docname,     str)

        # TODO improve
        pdflatex_args = [
                            self.pdflatex_bin,
                            '-disable-installer',
                            '-halt-on-error',
                            '-interaction=nonstopmode',
                            '-output-directory=%s' % (str(i_temp_folder)),
                            '%s.tex' % (i_docname),
                        ]

        # Switch the execution environment for pdflatex
        with self.pdflatex_env.setup():
            with subprocess.Popen(args  = pdflatex_args,
                                  cwd   = str(i_latex_folder),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc:
                stdout, stderr = proc.communicate()

                if proc.returncode:
                    if stdout:
                        stdout = stdout.decode('utf8')
                        print("\n\n\nSTDOUT: \n%s" % stdout)

                    if stderr:
                        stderr = stderr.decode('utf8')
                        print("\n\n\nSTDERR: \n%s" % stderr)

                    raise RuntimeError("Invokation of %s failed" % (self.pdflatex_bin))

    def _invoke_makeglossaries(self,
                               i_temp_folder  : Path,
                               i_docname      : str):
        assert isinstance(i_temp_folder, Path)
        assert isinstance(i_docname,     str)

        # TODO improve
        glossaries_args = [
                                self.glossaries_bin,
                                '%s' % (i_docname), # Note: use base name without extensions
                                '-t', 'makeglossaries-lite.log',
                               ]

        # Switch the execution environment for pdflatex
        with self.glossaries_env.setup():
            with subprocess.Popen(args  = glossaries_args,
                                  cwd   = str(i_temp_folder),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE) as proc:
                stdout, stderr = proc.communicate()

                if proc.returncode:
                    if stdout:
                        stdout = stdout.decode('utf8')
                        print("\n\n\nSTDOUT: \n%s" % stdout)

                    if stderr:
                        stderr = stderr.decode('utf8')
                        print("\n\n\nSTDERR: \n%s" % stderr)

                    raise RuntimeError("Invokation of %s failed" % (self.glossaries_bin))
