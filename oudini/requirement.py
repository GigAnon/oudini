#! python3

from    utils.logobj            import LogObj

import  xml.etree.ElementTree   as ETree
from    copy                    import deepcopy
from    enum                    import Enum
from    typing                  import Optional, Union
from    pathlib                 import Path
from    common_section          import CommonSection


class Requirement (LogObj):
    TAG_STR             = "req"
    ATTR_ID_STR         = "id"
    ATTR_SHORT_DESC_STR = "shortdesc"

    TEXT_TAG_STR    = "text"

    LINKS_TAG_STR   = "satisfies"

    VALIDATION_TAG_STR = "validation"

    class ValidationStrategy (Enum):
        Inspection      = "I"
        Analysis        = "A"
        Demonstration   = "D"
        Test            = "T"

    def __init__(self,
                 i_common : Optional[CommonSection] = None):
        assert isinstance(i_common, CommonSection) or i_common is None
        LogObj.__init__(self)

        self.id                  = None
        self.desc                = ""
        self.text                = ""
        self.validation_strategy = None
        self.common              = i_common # By reference

    def __bool__(self):
        return self.id is not None

    def to_xml(self) -> ETree.Element:

        # Mandatory fields
        assert self.id   is not None
        assert self.text is not None

        elt = ETree.Element(self.TAG_STR)

        elt.attrib[self.ATTR_ID_STR] = "{id:05d}".format(id = self.id)

        if (self.desc):
            elt.attrib[self.ATTR_SHORT_DESC_STR] = self.desc

        ETree.SubElement(elt,
                         self.TEXT_TAG_STR).text = self.text

        if (self.validation_strategy):
            ETree.SubElement(elt,
                             self.VALIDATION_TAG_STR).text = self.validation_strategy

        # TODO LINKS

        return elt


    @classmethod
    def from_xml_element(cls,
                         i_elt    : ETree.Element,
                         i_common : CommonSection):
        assert isinstance(i_elt,    ETree.Element)
        assert isinstance(i_common, CommonSection)
        assert i_elt.tag == cls.TAG_STR

        obj = cls(i_common = i_common)

        obj.id   = int(i_elt.get(obj.ATTR_ID_STR))
        obj.desc = deepcopy(i_elt.get(obj.ATTR_SHORT_DESC_STR))

        for e in i_elt:
            if      e.tag == obj.TEXT_TAG_STR:
                obj.text = e.text
            elif    e.tag == obj.LINKS_TAG_STR:
                pass # TODO LINKS
            elif    e.tag == obj.VALIDATION_TAG_STR:
                obj.validation_strategy = cls.ValidationStrategy(e.text)
            else:
                obj._logger.warning("<%s> tag ignored" % (e.tag))
                pass # Ignored tag
        return obj

    def get_snippet_filename(self,
                             i_root_folder     : Optional[Union[str,
                                                                Path]] = Path(),
                             i_fallback_format : Optional[str] = None):
        assert isinstance(i_root_folder, (str, Path))
        assert isinstance(i_fallback_format, str) or i_fallback_format is None

        if self.common.req_file_format:
            file_format = self.common.req_file_format
        elif i_fallback_format is not None:
            file_format = i_fallback_format
        else:
            raise Exception("No file format given")

        return Path(i_root_folder).joinpath(file_format.format(id = self.id))

    def format_id(self):
        if self.common is not None:
            return self.common.req_display_format.format(id = self.id)
        else:
            return str(self.id)

    def __str__(self):
        return self.format_id()

    def __repr__(self):
        s = "[%s] %s" % (self.format_id(), self.desc)
        if self.validation_strategy is not None:
            s += " %s" % (self.validation_strategy)

        return s
