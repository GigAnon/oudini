#! python3
import os
import xml.etree.ElementTree as ETree
from   copy                  import deepcopy
from   typing                import Optional
from   common_section        import CommonSection


class Requirement:
    REQ_TAG_STR             = "req"
    REQ_ATTR_ID_STR         = "id"
    REQ_ATTR_SHORT_DESC_STR = "shortdesc"

    TEXT_TAG_STR    = "text"

    LINKS_TAG_STR   = "satisfies"

    VALIDATION_TAG_STR = "validation"

    def __init__(self,
                 i_common : Optional[CommonSection] = None):
        assert isinstance(i_common, CommonSection) or i_common is None

        self.id                 = None
        self.desc                = ""
        self.text                = ""
        self.validation_strategy = None
        self.common = i_common # By reference

    def __bool__(self):
        return self.id is not None

    @classmethod
    def from_xml_element(cls,
                         i_elt    : ETree.Element,
                         i_common : CommonSection):
        assert isinstance(i_elt,    ETree.Element)
        assert isinstance(i_common, CommonSection)
        assert i_elt.tag == Requirement.REQ_TAG_STR

        obj = cls(i_common = i_common)

        obj.id   = int(i_elt.get(Requirement.REQ_ATTR_ID_STR))
        obj.desc = deepcopy(i_elt.get(Requirement.REQ_ATTR_SHORT_DESC_STR))

        for e in i_elt:
            if      e.tag == Requirement.TEXT_TAG_STR:
                obj.text = e.text
            elif    e.tag == Requirement.LINKS_TAG_STR:
                pass
            elif    e.tag == Requirement.VALIDATION_TAG_STR:
                obj.validation_strategy = e.text # TODO ENUM
            else:
                pass # Ignored tag
        return obj

    def get_snippet_filename(self,
                             i_root_folder     : Optional[str] = "",
                             i_fallback_format : Optional[str] = None):
        assert isinstance(i_root_folder,     str) or i_root_folder     is None
        assert isinstance(i_fallback_format, str) or i_fallback_format is None

        if self.common.req_file_format:
            file_format = self.common.req_file_format
        elif i_fallback_format is not None:
            file_format = i_fallback_format
        else:
            raise Exception("No file format given")

        return os.path.join(i_root_folder, file_format.format(id = self.id))

    def format_id(self):
        if self.common is not None:
            return self.common.req_display_format.format(id = self.id)
        else:
            return str(self.id)

    def __str__(self):
        s = "[%s] %s" % (self.format_id(), self.desc)
        if self.validation_strategy is not None:
            s += " %s" % (self.validation_strategy)

        return s

    def __repr__(self):
        return self.__str__()
