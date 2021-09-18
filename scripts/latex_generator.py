#! python3

from    generator       import Generator
from    requirement     import Requirement
from    common_section  import CommonSection
from    typing          import Optional
from    glossary        import Glossary


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

    def __init__(self):
        super().__init__()

    def generate_requirement(self,
                             i_req      : Requirement,
                             i_filename : Optional[str] = None) -> str:
        assert isinstance(i_req,        Requirement)
        assert isinstance(i_filename,   str) or i_filename is None

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
            with open(i_filename, mode = 'w') as file:
                file.write(text)

        return text


    def generate_constants(self,
                           i_common   : CommonSection,
                           i_filename : Optional[str] = None) -> str:
        assert isinstance(i_filename,   str) or i_filename is None
        assert isinstance(i_filename,   str) or i_filename is None

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
            with open(i_filename, mode = 'w') as file:
                file.write(text)

        return text


    def generate_glossary(self,
                          i_glossary : Glossary,
                          i_filename : Optional[str] = None) -> str:
        assert isinstance(i_glossary,   Glossary)
        assert isinstance(i_filename,   str) or i_filename is None

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
            with open(i_filename, mode = 'w') as file:
                file.write(text)

        return text
