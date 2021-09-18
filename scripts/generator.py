#! python3

from requirement        import Requirement
from common_section     import CommonSection
from typing             import Optional
from glossary           import Glossary


class Generator:
    DEFAULT_REQ_FILE_FORMAT       = "{id:05d}.txt"
    DEFAULT_CONSTANTS_FILE_FORMAT = "constants.txt"
    DEFAULT_GLOSSARY_FILE_FORMAT  = "glossary.txt"

    def __init__(self):
        pass

    def generate_requirement(self,
                             i_req      : Requirement,
                             i_filename : Optional[str] = None):
        assert isinstance(i_req,        Requirement)
        assert isinstance(i_filename,   str) or i_filename is None
        raise NotImplementedError()


    def generate_constants(self,
                           i_common   : CommonSection,
                           i_filename : Optional[str] = None):
        assert isinstance(i_common,     str) or i_filename is None
        assert isinstance(i_filename,   str) or i_filename is None
        raise NotImplementedError()

    def generate_glossary(self,
                          i_glossary : Glossary,
                          i_filename : Optional[str] = None) :
        assert isinstance(i_filename,   str) or i_filename is None
        raise NotImplementedError()
