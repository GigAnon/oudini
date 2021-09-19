#! python3
import shutil
import logging

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
                 i_document         : Document,
                 i_project_root_dir : Union[str,
                                            Path] = Path(),
                 i_compiler         : Optional[Compiler] = None):
        super().__init__(i_document         = i_document,
                         i_project_root_dir = i_project_root_dir,
                         i_compiler         = i_compiler)

        self.latex_root_dir = self.root_dir.joinpath('latex')       # TODO constant / improve?
        self.snip_root_dir  = self.latex_root_dir.joinpath('snip') # TODO constant / improve?

        self._logger.info("Created LaTex generator with compiler '%s'" % (type(i_compiler).__name__))


    def _generate_requirement(self,
                              i_req      : Requirement,
                              i_filename : Optional[Union[str,
                                                          Path]] = None) -> str:
        assert isinstance(i_req,        Requirement)
        assert isinstance(i_filename,   str)    or \
               isinstance(i_filename,   Path)   or \
               i_filename is None

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
            self._logger.debug("Writing [{req}] into '{file}'".format(req  = i_req.format_id(),
                                                                      file = i_filename.name))
            with open(i_filename, mode = 'w') as file:
                file.write(text)

        return text


    def _generate_constants(self,
                            i_common   : CommonSection,
                            i_filename : Optional[Union[str,
                                                        Path]] = None) -> str:
        assert isinstance(i_common,     CommonSection)
        assert isinstance(i_filename,   str)    or \
               isinstance(i_filename,   Path)   or \
               i_filename is None

        # TODO read from XML
        toto = {
                'projectTitlePretty'     : 'MY SUPER PROJECT',
                'documentTitlePretty'    : 'MY SUPER DOCUMENT',
                'documentUidPretty'      : 'UID',
                'documentCategoryPretty' : 'Category ??',
                }

        text = ""
        for k, v in toto.items():
            text += LatexGenerator.LATEX_CONSTANT_TEMPLATE.format(constant_name  = k,
                                                                  constant_value = v)

        if i_filename is not None:
            self._logger.debug("Writing constantes into '{file}'".format(file = i_filename.name))
            with open(i_filename, mode = 'w') as file:
                file.write(text)

        return text


    def _generate_glossary(self,
                           i_glossary : Glossary,
                           i_filename : Optional[Union[str,
                                                       Path]] = None) -> str:
        assert isinstance(i_glossary,   Glossary)
        assert isinstance(i_filename,   str)    or \
               isinstance(i_filename,   Path)   or \
               i_filename is None

        acronyms = ""
        for a in i_glossary.acronyms.values():
            assert isinstance(a, Glossary.Acronym)
            acronyms += LatexGenerator.LATEX_GLOSSARY_ACRONYM_TEMPLATE.format(uid         = a.uid,
                                                                              description = a.description,
                                                                              shorthand   = a.shorthand or a.uid)

        definitions = ""
        for a in i_glossary.definitions.values():
            assert isinstance(a, Glossary.Definition)
            definitions += LatexGenerator.LATEX_GLOSSARY_DEFINITION_TEMPLATE.format(uid         = a.uid,
                                                                                    description = a.description)

        text = LatexGenerator.LATEX_GLOSSARY_GLOBAL_TEMPLATE.format(definitions = definitions,
                                                                    acronyms    = acronyms)

        if i_filename is not None:
            self._logger.debug("Writing glossary into '{file}'".format(file = i_filename.name))
            with open(i_filename, mode = 'w') as file:
                file.write(text)

        return text

    def generate_and_compile(self,
                             i_out_dir          : Union[str, Path],
                             i_clean_before_run : Optional[bool] = True):
        assert isinstance(i_out_dir, str)   or \
               isinstance(i_out_dir, Path)
        assert isinstance(i_clean_before_run, bool)

        # If requested, delete the output folder first
        if i_clean_before_run:
            self._logger.info("Deleting '{dir}'".format(dir = i_out_dir))
            shutil.rmtree(i_out_dir, ignore_errors = True)

        # Snippet generation is done in the LaTeX / snip folder
        self.generate_document(i_document    = self.document,
                               i_root_folder = self.snip_root_dir)

        if self.compiler is None:
            raise Exception("No LaTeX compiler specified")

        self.compiler.run(i_document     = self.document,
                          i_doc_root_dir = self.latex_root_dir,
                          i_output_dir   = i_out_dir)

