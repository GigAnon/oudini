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

    VALIDATION_TAG_STR = "validation"

    class LinkRef:
        TAG_STR         = "satisfies"
        ATTR_SOURCE_STR = "source"
        ATTR_ID_STR     = "id"

        def __init__(self,
                     i_source : str = "",
                     i_id     : str = ""):
            assert isinstance(i_source, str), f"i_source is {type(i_source)}"
            assert isinstance(i_id,     str), f"i_id is {type(i_id)}"
            self.source = i_source
            self.id     = i_id

        @classmethod
        def from_xml_element(cls,
                             i_elt    : ETree.Element):
            assert isinstance(i_elt, ETree.Element), f"type(i_elt) is {type(i_elt)}"
            assert i_elt.tag == cls.TAG_STR

            if not (src := i_elt.get(cls.ATTR_SOURCE_STR)):
                raise Exception(f"Missing mandatory field <{cls.ATTR_SOURCE_STR}> in <{cls.TAG_STR}>")

            if not (req_id := i_elt.get(cls.ATTR_ID_STR)):
                raise Exception(f"Missing mandatory field <{cls.ATTR_ID_STR}> in <{cls.TAG_STR}>")

            return cls(i_source = src,
                       i_id     = req_id)

        def to_xml(self) -> ETree.Element:
            elt = ETree.Element(self.TAG_STR)
            elt.attrib[self.ATTR_ID_STR]     = self.id
            elt.attrib[self.ATTR_SOURCE_STR] = self.source
            return elt


    class ValidationStrategy (Enum):
        Inspection      = "I"
        Analysis        = "A"
        Demonstration   = "D"
        Test            = "T"

    def __init__(self,
                 i_common : Optional[CommonSection] = None):
        assert isinstance(i_common, (CommonSection, type(None))), f"type(i_common) is {type(i_common)}"
        LogObj.__init__(self)

        self.id                  = None
        self.desc                = ""
        self.text                = ""
        self.validation_strategy = None
        self.common              = i_common # By reference
        self.links               = []

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
                             self.VALIDATION_TAG_STR).text = self.validation_strategy.value

        for lnk in self.links:
            elt.append(lnk.to_xml())

        return elt


    @classmethod
    def from_xml_element(cls,
                         i_elt    : ETree.Element,
                         i_common : CommonSection):
        assert isinstance(i_elt,    ETree.Element), f"type(i_elt) is {type(i_elt)}"
        assert isinstance(i_common, CommonSection), f"type(i_common) is {type(i_common)}"
        assert i_elt.tag == cls.TAG_STR, f"i_elt.tag is <{i_elt.tag}>"

        obj = cls(i_common = i_common)

        if (id_str := i_elt.get(obj.ATTR_ID_STR)) is not None:
            obj.id = int(id_str)
        else:
            raise Exception(f"Missing mandatory field <{obj.ATTR_ID_STR}> in <{obj.TAG_STR}>")

        if (desc := i_elt.get(obj.ATTR_SHORT_DESC_STR)) is not None:
            obj.desc = deepcopy(desc)
        else:
            raise Exception(f"Missing mandatory field <{obj.ATTR_SHORT_DESC_STR}> in <{obj.TAG_STR}>")

        for e in i_elt:
            if      e.tag == obj.TEXT_TAG_STR:
                obj.text = e.text
            elif    e.tag == obj.LinkRef.TAG_STR:
                obj.links.append(obj.LinkRef.from_xml_element(e))
            elif    e.tag == obj.VALIDATION_TAG_STR:
                obj.validation_strategy = obj.ValidationStrategy(e.text)
            else:
                obj._w(f"<{e.tag}> tag ignored")
                pass # Ignored tag
        return obj

    def get_snippet_filename(self,
                             i_root_folder     : Optional[Union[str,
                                                                Path]] = Path(),
                             i_fallback_format : Optional[str] = None):
        assert isinstance(i_root_folder, (str, Path)),           f"type(i_root_folder) is {type(i_root_folder)}"
        assert isinstance(i_fallback_format, (str, type(None))), f"type(i_fallback_format) is {type(i_fallback_format)}"

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
        s = f"[{self.format_id()}] {self.desc}"
        if self.validation_strategy is not None:
            s += " %s" % (self.validation_strategy)

        return s
