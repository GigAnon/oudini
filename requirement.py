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

    def __init__(self,
                 i_common : Optional[CommonSection] = None):
        assert isinstance(i_common, CommonSection) or i_common is None

        self.id     = None
        self.desc   = ""
        self.text   = ""
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
            else:
                pass # Ignored tag
        return obj

    def generate(self,
                 i_file_generator,
                 i_root_folder   : str):
        assert isinstance(i_root_folder,    str)

        self._generate_self(i_file_generator = i_file_generator,
                            i_filename       = self._get_snippet_filename(i_root_folder = i_root_folder))



    def _get_snippet_filename(self,
                              i_root_folder : str):
        if self.common.req_file_format:
            file_format = self.common.req_file_format
        else:
            file_format = CommonSection.DEFAULT_REQ_FILE_FORMAT

        return os.path.join(i_root_folder, file_format.format(id = self.id))

    def _generate_self(self,
                       i_file_generator,
                       i_filename      : str):
        assert isinstance(i_filename, str)

        i_file_generator.generate_requirement(i_req      = self,
                                              i_filename = i_filename)

    def format_id(self):
        if self.common is not None:
            return self.common.req_display_format.format(id = self.id)
        else:
            return str(self.id)

    def __str__(self):
        return "[%s] %s" % (self.format_id(), self.desc)

    def __repr__(self):
        return self.__str__()
