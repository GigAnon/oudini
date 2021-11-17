#! python3
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
        assert isinstance(i_miktex_bin_dir, (str, Path)) or \
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

        self._logger.info("Created MikTex compiler")
        self._logger.debug(f"MikTex bin dir : {self.miktex_bin_dir}")


    def run(self,
            i_doc_root_dir: Union[str, Path],
            i_output_dir  : Union[str, Path],
            i_document    : Optional[Document]) -> None:
        assert isinstance(i_document, Document) or i_document is None
        assert isinstance(i_doc_root_dir, str) or \
               isinstance(i_doc_root_dir, Path)
        assert isinstance(i_output_dir, str) or \
               isinstance(i_output_dir, Path)

        if isinstance(i_output_dir, str):
            i_output_dir = Path(i_output_dir)

        self._logger.info(f"Running document compilation for [{i_document.common.project!r}:{'TODO'}]")

        # TODO better system
        LATEX_MAIN_DOC_NAME = "main"
        output_filename     = f"{LATEX_MAIN_DOC_NAME}.pdf"
        output_file         = i_output_dir.joinpath(output_filename)

        output_tmp_dir      = i_output_dir.joinpath('tmp')
        output_tmp_file     = output_tmp_dir.joinpath(output_filename)

        self._logger.debug(f"Removing f'{output_tmp_dir}'")
        shutil.rmtree(path          = output_tmp_dir,
                      ignore_errors = True)

        self._logger.debug(f"Removing '{output_filename}'")
        try:
            output_file.unlink(missing_ok = True)
        except PermissionError:
            self._logger.error(f"Could not delete '{output_file}'")
            pass

        self._logger.info(f"[1/3] Running {self.pdflatex_bin}")
        self._invoke_pdflatex(i_latex_folder = i_doc_root_dir,
                              i_temp_folder  = output_tmp_dir,
                              i_docname      = LATEX_MAIN_DOC_NAME)

        self._logger.info(f"[1/1] Running {self.glossaries_bin}")
        self._invoke_makeglossaries(i_temp_folder  = output_tmp_dir,
                                    i_docname      = LATEX_MAIN_DOC_NAME)

        self._logger.info(f"[2/3] Running {self.pdflatex_bin}")
        self._invoke_pdflatex(i_latex_folder = i_doc_root_dir,
                              i_temp_folder  = output_tmp_dir,
                              i_docname      = LATEX_MAIN_DOC_NAME)

        self._logger.info(f"[3/3] Running {self.pdflatex_bin}")
        self._invoke_pdflatex(i_latex_folder = i_doc_root_dir,
                              i_temp_folder  = output_tmp_dir,
                              i_docname      = LATEX_MAIN_DOC_NAME)

        self._logger.info(f"Copying '{output_tmp_file}' to '{output_file}'")
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
                            f'-output-directory={i_temp_folder!s}',
                            f'{i_docname}.tex',
                        ]

        self._logger.debug("Invoking {bin} in {folder}".format(bin    = self.pdflatex_bin,
                                                               folder = str(i_latex_folder)))
        self._logger.debug("Args: %s" % (repr(pdflatex_args)))

        # Switch the execution environment for pdflatex
        with self.pdflatex_env.setup(i_cwd = i_latex_folder):
            with subprocess.Popen(args  = pdflatex_args,
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

                    self._logger.critical("Invokation of {bin} failed".format(bin = self.pdflatex_bin))
                    raise RuntimeError("Invokation of {bin} failed".format(bin = self.pdflatex_bin))
                else:
                    self._logger.debug("Invokation of {bin} successfull".format(bin = self.pdflatex_bin))

    def _invoke_makeglossaries(self,
                               i_temp_folder  : Path,
                               i_docname      : str):
        assert isinstance(i_temp_folder, Path)
        assert isinstance(i_docname,     str)

        # TODO improve
        glossaries_args = [
                            self.glossaries_bin,
                            f'{i_docname}',
                            '-t', 'makeglossaries-lite.log',
                          ]

        self._logger.debug("Invoking {bin} in {folder}".format(bin    = self.glossaries_bin,
                                                               folder = str(i_temp_folder)))
        self._logger.debug("Args: %s" % (repr(glossaries_args)))

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

                    self._logger.critical("Invokation of {bin} failed".format(bin = self.glossaries_bin))
                    raise RuntimeError("Invokation of {bin} failed".format(bin = self.glossaries_bin))
                else:
                    self._logger.debug("Invokation of {bin} successfull".format(bin = self.glossaries_bin))
