#! python3

from    generator      import Generator
from    requirement    import Requirement


class LatexGenerator (Generator):
    LATEX_REQ_TEMPLATE =\
r"""
\level{{4}}{{ {short_descr} }} \label{{ {display_name} }}
\begin{{requirement}}{{ {display_name} }}
{text}
\end{{requirement}}
"""

    def __init__(self):
        pass

    def generate_requirement(self,
                             i_req      : Requirement,
                             i_filename : str):
        assert isinstance(i_req,        Requirement)
        assert isinstance(i_filename,   str)

        text = LatexGenerator.LATEX_REQ_TEMPLATE.format(text         = i_req.text,
                                                        display_name = i_req.format_id(),
                                                        short_descr  = i_req.desc)

        print(text)

        with open(i_filename, mode = 'w') as file:
            file.write(text)

