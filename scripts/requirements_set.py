#! python3

import  xml.etree.ElementTree   as ETree
from    copy                    import deepcopy
from    typing                  import Optional
from    requirement             import Requirement
from    common_section          import CommonSection


class RequirementsSet:
    REQ_SET_TAG_STR = "requirements"

    SECTION_TAG_STR = "sec"

    def __init__(self,
                 i_common : Optional[CommonSection] = None):
        assert isinstance(i_common, CommonSection) or i_common is None

        self.reqs   = {}
        self.common = i_common # By reference

    @classmethod
    def from_xml_element(cls,
                         i_elt    : ETree.Element,
                         i_common : CommonSection):
        assert isinstance(i_elt,    ETree.Element)
        assert isinstance(i_common, CommonSection)
        assert i_elt.tag == RequirementsSet.REQ_SET_TAG_STR

        obj = cls(i_common = i_common)

        # Recursively walk through sections to flatten out the requirements
        # (depth should be reasonable)
        obj._walk_xml_add_reqs(i_section = i_elt)

        return obj

    def _walk_xml_add_reqs(self,
                           i_section : ETree.Element):
        assert isinstance(i_section, ETree.Element)

        for e in i_section:
            if   e.tag == Requirement.REQ_TAG_STR:
                r = Requirement.from_xml_element(i_elt      = e,
                                                 i_common   = self.common)
                self.reqs[r.id] = r
            elif e.tag == RequirementsSet.SECTION_TAG_STR:
                self._walk_xml_add_reqs(i_section = e)

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        s = ""
        if len(self.reqs) > 0:
            s += "%u requirements in set:\n" % (len(self.reqs))
            for _, v in self.reqs.items():
                s += "%s\n" % (repr(v))
        else:
            s += "No requirements in set"
        return s
