#! python3

import xml.etree.ElementTree as ETree
from   copy                  import deepcopy
from   typing                import Optional


class CommonSection:
    COMMON_TAG_STR              = "general"
    REQDISPLAYFORMAT_TAG_STR    = "reqdisplayformat"
    REQFILEFORMAT_TAG_STR       = "reqfileformat"

    PROJECT_TAG_STR             = "project"
    PROJECT_ATTR_INTERNAL_STR   = "internal"
    PROJECT_ATTR_PRETTY_STR     = "pretty"

    DEFAULT_REQ_FILE_FORMAT     = "{id:05d}.tex"

    class Project:
        def __init__(self,
                     i_internal_name: str,
                     i_pretty_name  : Optional[str] = None):
            assert isinstance(i_internal_name, str)
            assert isinstance(i_pretty_name,   str) or i_pretty_name is None

            self.internal = i_internal_name
            self.pretty   = i_pretty_name

        def __str__(self):
            return self.internal

        def __repr__(self):
            return self.pretty or self.internal


    def __init__(self):
        self.project            = None
        self.req_display_format = ""
        self.req_file_format    = ""

    @classmethod
    def from_xml_element(cls,
                         i_elt : ETree.Element):
        assert isinstance(i_elt, ETree.Element)
        assert i_elt.tag == CommonSection.COMMON_TAG_STR

        obj = cls()

        for e in i_elt:
            if      e.tag == CommonSection.REQDISPLAYFORMAT_TAG_STR:
                obj.req_display_format = e.text
            elif    e.tag == CommonSection.REQFILEFORMAT_TAG_STR:
                obj.req_file_format = e.text
            elif    e.tag == CommonSection.PROJECT_TAG_STR:
                pass
            else:
                pass # Ignored tag

        return obj

    def __str__(self):
        s = ""
        s += repr(self.project)
        return s

    def __repr__(self):
        return self.__str__()
