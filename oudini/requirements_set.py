#! python3
from    utils.logobj            import LogObj
import  xml.etree.ElementTree   as ETree
from    collections             import OrderedDict
from    typing                  import Optional
from    typing                  import Union
from    requirement             import Requirement
from    common_section          import CommonSection


class RequirementsSet (LogObj):
    TAG_STR = "requirements"

    SECTION_TAG_STR = "sec"

    def __init__(self,
                 i_common    : Optional[CommonSection] = None,
                 i_req_class : Optional[Requirement]   = Requirement):
        assert isinstance(i_common, CommonSection) or i_common is None
        LogObj.__init__(self)

        self._req_class = i_req_class
        self.reqs       = OrderedDict()
        self.common     = i_common # By reference

    def to_xml(self) -> ETree.Element:
        root = ETree.Element(self.TAG_STR)
        for _, r in self.reqs.items():
            root.append(r.to_xml())
        return root

    @classmethod
    def from_xml_element(cls,
                         i_elt    : ETree.Element,
                         i_common : CommonSection):
        assert isinstance(i_elt,    ETree.Element)
        assert isinstance(i_common, CommonSection)
        assert i_elt.tag == cls.TAG_STR

        obj = cls(i_common = i_common)

        # Recursively walk through sections to flatten out the requirements
        # (depth should be reasonable)
        obj._walk_xml_add_reqs(i_section = i_elt)
        obj._logger.debug(f"Created from XML ({len(obj.reqs)} reqs)")

        return obj

    def _walk_xml_add_reqs(self,
                           i_section : ETree.Element):
        assert isinstance(i_section, ETree.Element)

        # TODO save sections
        for e in i_section:
            if   e.tag == self._req_class.TAG_STR:
                r = self._req_class.from_xml_element(i_elt      = e,
                                                     i_common   = self.common)
                assert r.id not in self.reqs
                self.reqs[r.id] = r
            elif e.tag == RequirementsSet.SECTION_TAG_STR:
                self._walk_xml_add_reqs(i_section = e)

    def __contains__(self,
                     i_key : Union[str, Requirement]):
        assert isinstance(i_key, (Requirement, str))

        if (isinstance(i_key, Requirement)):
            return i_key in self.reqs.values()
        return i_key in self.reqs

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        s = ""
        if len(self.reqs) > 0:
            s += f"{len(self.reqs)} requirements in set:\n"
            for _, v in self.reqs.items():
                s += f"{v!r}\n"
        else:
            s += "No requirements in set"
        return s
