#! python3
import shutil

from    generator       import Generator
from    compiler        import Compiler
from    requirement     import Requirement
from    common_section  import CommonSection
from    glossary        import Glossary
from    document        import Document

from    pathlib         import Path
from    typing          import Optional
from    typing          import Union


class LatexGenerator (Generator):
    """
        LaTeX document generator
    """

    DEFAULT_REQ_FILE_FORMAT       = "{id:05d}.tex"
    DEFAULT_CONSTANTS_FILE_FORMAT = "constants.tex"
    DEFAULT_GLOSSARY_FILE_FORMAT  = "glossary.tex"

    LATEX_REQ_TEMPLATE =\
r"""
\level{{4}}{{ {short_descr} }} \label{{{label_name}}}
\begin{{requirement}}{{{display_name}}} {validation_strategy}
{text}
\end{{requirement}}
"""
    LATEX_VALIDATION_STRATEGY_TEMPLATE =\
r"""
[\textbf{{\color{{blue}} {text} }}]
"""

    LATEX_CONSTANT_TEMPLATE =\
r"""
\newcommand{{\{constant_name}}} {{{constant_value}\xspace}}
"""

    LATEX_GLOSSARY_GLOBAL_TEMPLATE =\
r"""
\makeglossaries
{definitions}
{acronyms}
"""

    LATEX_GLOSSARY_ACRONYM_TEMPLATE =\
r"""
\newacronym{{{uid}}}{{{shorthand}}}{{{description}}}
"""

    LATEX_GLOSSARY_DEFINITION_TEMPLATE =\
r"""
\newglossaryentry{{{uid}}}
{{
    name={{{uid}}},
    description={{{description}}}
}}
"""

    def __init__(self,
                 i_project_root_dir : Union[str,
                                            Path] = Path(),
                 i_compiler         : Optional[Compiler] = None):
        """
            Constructor.
        :param i_project_root_dir: Root of the LaTeX project (i.e. where the .tex root document is)
        :param i_compiler        : LaTeX compiler to use for document generation
        """

        super().__init__(i_project_root_dir = i_project_root_dir,
                         i_compiler         = i_compiler)

        self.latex_root_dir = self.root_dir.joinpath('latex')       # TODO constant / improve?
        self.snip_root_dir  = self.latex_root_dir.joinpath('snip') # TODO constant / improve?

        self._i("Created LaTex generator with compiler '%s'" % (type(i_compiler).__name__))


    def _generate_requirement(self,
                              i_req      : Requirement,
                              i_filename : Optional[Union[str,
                                                          Path]] = None) -> str:
        """
            Generate a .tex file (snippet) containing formated LaTeX input for requirement i_req.
            This file can then be included into a master LaTeX document.

        :param i_req     : Oudini requirement to convert to LaTeX
        :param i_filename: Filename where to write the snippet (optional)
        :return          : Generated LaTeX code
        """
        assert isinstance(i_req,        Requirement),             f"type(i_req) is {type(i_req)}"
        assert isinstance(i_filename,   (str, Path, type(None))), f"type(i_filename) is {type(i_filename)}"

        if i_req.validation_strategy is not None:
            validation_strategy = LatexGenerator.LATEX_VALIDATION_STRATEGY_TEMPLATE.format(text = i_req.validation_strategy)
        else:
            validation_strategy = ""

        text = LatexGenerator.LATEX_REQ_TEMPLATE.format(text                = i_req.text,
                                                        display_name        = i_req.format_id(),
                                                        label_name          = i_req.format_id(),
                                                        short_descr         = i_req.desc,
                                                        validation_strategy = validation_strategy)

        if i_filename is not None:
            self._d("Writing [{req}] into '{file}'".format(req  = i_req.format_id(),
                                                                      file = i_filename.name))
            with open(i_filename, mode = 'w') as file:
                file.write(text)

        return text


    def _generate_constants(self,
                            i_common   : CommonSection,
                            i_filename : Optional[Union[str,
                                                        Path]] = None) -> str:
        """
        Generate a .tex file containing a LaTeX-compatible definition of the constants provided by
        the requirement database 'common' section

        :param i_common  : 'Common' section of the requirement database
        :param i_filename: Name for the .tex file the constants will be defined into. If none is provided, perform a dry run.
        :return: The content of the generated LaTeX code
        """
        assert isinstance(i_common,     CommonSection),           f"type(i_common) is {type(i_common)}"
        assert isinstance(i_filename,   (str, Path, type(None))), f"type(i_filename) is {type(i_filename)}"

        constants = {
                        'projectTitlePretty'     : repr(i_common.project) if i_common.project else "UNDEFINED PROJECT",
                        'documentTitlePretty'    : repr(i_common.title)   if i_common.title   else "UNDEFINED DOCUMENT",
                        'documentUidPretty'      : "UID GOES HERE", # TODO read from XML
                        'documentCategoryPretty' : "???",
                    }


        text = ""
        for k, v in constants.items():
            text += LatexGenerator.LATEX_CONSTANT_TEMPLATE.format(constant_name  = k,
                                                                  constant_value = LatexGenerator.sanitize(v))

        if i_filename is not None:
            self._d(f"Writing constants into '{i_filename.name}'")
            with open(i_filename, mode = 'w') as file:
                file.write(text)

        return text


    def _generate_glossary(self,
                           i_glossary : Glossary,
                           i_filename : Optional[Union[str,
                                                       Path]] = None) -> str:
        assert isinstance(i_glossary,   Glossary),                f"type(i_glossary) is {type(i_glossary)}"
        assert isinstance(i_filename,   (str, Path, type(None))), f"type(i_filename) is {type(i_filename)}"

        acronyms    = ""
        definitions = ""
        for a in i_glossary.definitions.values():
            assert isinstance(a, Glossary.Definition), f"type(a) is {type(a)}"

            if isinstance(a, Glossary.Acronym):
                acronyms += LatexGenerator.LATEX_GLOSSARY_ACRONYM_TEMPLATE.format(uid         = a.uid,
                                                                                  description = a.description,
                                                                                  shorthand   = a.shorthand or a.uid)
            else:
                definitions += LatexGenerator.LATEX_GLOSSARY_DEFINITION_TEMPLATE.format(uid         = a.uid,
                                                                                        description = a.description)

        text = LatexGenerator.LATEX_GLOSSARY_GLOBAL_TEMPLATE.format(definitions = definitions,
                                                                    acronyms    = acronyms)

        if i_filename is not None:
            self._d(f"Writing glossary into '{i_filename.name}'")
            with open(i_filename, mode = 'w') as file:
                file.write(text)

        return text

    def generate_and_compile(self,
                             i_document         : Document,
                             i_out_dir          : Union[str, Path],
                             i_clean_before_run : Optional[bool] = True):
        assert isinstance(i_document,           Document),      f"type(i_document) is {type(i_document)}"
        assert isinstance(i_out_dir,            (str, Path)),   f"type(i_document) is {type(i_out_dir)}"
        assert isinstance(i_clean_before_run,   bool),          f"type(i_clean_before_run) is {type(i_clean_before_run)}"

        # If requested, delete the output folder first
        if i_clean_before_run:
            self._i(f"Deleting '{i_out_dir}'")
            shutil.rmtree(i_out_dir, ignore_errors = True)

        # Snippet generation is done in the LaTeX / snip folder
        self.generate_document(i_document    = i_document,
                               i_root_folder = self.snip_root_dir)

        if self.compiler is None:
            raise Exception("No LaTeX compiler specified")

        self.compiler.run(i_document     = i_document,
                          i_doc_root_dir = self.latex_root_dir,
                          i_output_dir   = i_out_dir)

    @staticmethod
    def sanitize(i_str: str):
        """
        Escape the characters of i_str to make it LaTeX-friendly.

        The following characters will be escaped: & % $ # _ { } ~ ^ \

        :param i_str: String to be sanized (escaped)
        :return:      Sanitized string
        """
        # Backslashes must be escaped first
        i_str = i_str.replace('\\', r'\textbackslash')

        return i_str.replace('&',  r'\&')                  \
                    .replace('%',  r'\%')                  \
                    .replace('$',  r'\$')                  \
                    .replace('_',  r'\_')                  \
                    .replace('{',  r'\{')                  \
                    .replace('}',  r'\}')                  \
                    .replace('~',  r'\textasciitilde')     \
                    .replace('^',  r'\textasciicircum')

