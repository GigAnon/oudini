#! python3
import  logging
import  xml.etree.ElementTree   as ETree
from    typing                  import Optional
from    typing                  import Union
from    pathlib                 import Path


class CommonSection:
    TAG_STR                     = "general"
    REQDISPLAYFORMAT_TAG_STR    = "reqdisplayformat"
    REQFILEFORMAT_TAG_STR       = "reqfileformat"

    class _PT:
        TAG_STR           = None
        ATTR_INTERNAL_STR = "internal"
        ATTR_PRETTY_STR   = "pretty"

        def __init__(self,
                     i_internal_name: str,
                     i_pretty_name  : Optional[str] = None):
            assert isinstance(i_internal_name,  str)
            assert isinstance(i_pretty_name,    str) or i_pretty_name is None

            self.internal       = i_internal_name
            self.pretty         = i_pretty_name

        def to_xml(self) -> ETree.Element:
            elt = ETree.Element(self.TAG_STR)
            if self.internal is not None:
                elt.attrib[self.ATTR_INTERNAL_STR] = self.internal
            if self.internal is not None:
                elt.attrib[self.ATTR_PRETTY_STR]   = self.pretty
            return elt

        @classmethod
        def from_xml_element(cls,
                             i_elt : ETree.Element):
            assert isinstance(i_elt, ETree.Element)
            assert i_elt.tag == cls.TAG_STR
            return cls(i_internal_name = i_elt.get(cls.ATTR_INTERNAL_STR,  default = None),
                       i_pretty_name   = i_elt.get(cls.ATTR_PRETTY_STR,   default = None))

        def __str__(self):
            return self.internal

        def __repr__(self):
            return self.pretty or self.internal

    class Project (_PT):
        TAG_STR = "project"

    class Title (_PT):
        TAG_STR = "title"

    class People:
        TAG_STR              = "people"
        PERSON_TAG_STR       = "person"
        PERSON_ATTR_ROLE_STR = "role"

        class Elt:
            def __init__(self,
                         i_name: str,
                         i_role: str):
                assert isinstance(i_name, str)
                assert isinstance(i_role, str)
                self.name = i_name
                self.role = i_role

            def to_xml(self) -> ETree.Element:
                elt = ETree.Element(CommonSection.People.PERSON_TAG_STR)
                elt.text = self.name
                elt.attrib[CommonSection.People.PERSON_ATTR_ROLE_STR] = self.role
                return elt

            def __str__(self):
                return "'%s' ('%s')" % (self.name, self.role)

            def __repr__(self):
                return self.__str__()

        def __init__(self):
            self._logger = logging.getLogger("%s-%s" % (__name__, type(self).__name__))
            self.list = []

        def to_xml(self) -> ETree.Element:
            root = ETree.Element(self.TAG_STR)
            for p in self.list:
                root.append(p.to_xml())
            return root

        @classmethod
        def from_xml_element(cls,
                             i_elt : ETree.Element):
            assert isinstance(i_elt, ETree.Element)
            assert i_elt.tag == cls.TAG_STR

            obj = cls()

            for e in i_elt:
                if      e.tag == cls.PERSON_TAG_STR:
                    obj.list.append(CommonSection.People.Elt(i_name = e.text.strip(),
                                                             i_role = e.get(cls.PERSON_ATTR_ROLE_STR).strip()))
                    obj._logger.debug("Section (<%s>) : '%s' ('%s')", cls.PERSON_TAG_STR,
                                                                      obj.list[-1].name,
                                                                      obj.list[-1].role)
                else:
                    obj._logger.warning("Ignoring unknown section <%s>" % (e.tag))
                    pass # Ignored tag

            obj._logger.debug("Created from XML : %s" % (repr(obj)))

            return obj

        def __str__(self):
            return str(self.list)

        def __repr__(self):
            return repr(self.list)

    def __init__(self):
        self._logger = logging.getLogger("%s-%s" % (__name__, type(self).__name__))

        self.project                = None
        self.title                  = None
        self.people                 = None
        self.req_display_format     = None
        self.req_file_format        = None
        self.constants_file_format  = None

    def to_xml(self) -> ETree.Element:
        root = ETree.Element(self.TAG_STR)

        for e in [ self.project, self.title, self.people ]:
            if e is not None:
                root.append(e.to_xml())

        return root

    @classmethod
    def from_xml_element(cls,
                         i_elt : ETree.Element):
        assert isinstance(i_elt, ETree.Element)
        assert i_elt.tag == cls.TAG_STR

        obj = cls()
        obj._logger.debug(f"Instanciating '{cls.__name__}'")

        for e in i_elt:
            if      e.tag == cls.REQDISPLAYFORMAT_TAG_STR:
                obj._logger.debug("Found requirement display format section (<%s>)", cls.REQDISPLAYFORMAT_TAG_STR)
                obj.req_display_format = e.text

            elif    e.tag == CommonSection.REQFILEFORMAT_TAG_STR:
                obj._logger.debug("Found requirement file format section (<%s>)", CommonSection.REQFILEFORMAT_TAG_STR)
                obj.req_file_format = e.text

            elif    e.tag == CommonSection.Project.TAG_STR:
                obj._logger.debug("Found project info section (<%s>)", CommonSection.Project.TAG_STR)
                obj.project = CommonSection.Project.from_xml_element(e)
                obj._logger.debug(repr(obj.project))

            elif    e.tag == CommonSection.Title.TAG_STR:
                obj._logger.debug("Found document title info section (<%s>)", CommonSection.Title.TAG_STR)
                obj.title = CommonSection.Title.from_xml_element(e)
                obj._logger.debug(repr(obj.title))

            elif    e.tag == CommonSection.People.TAG_STR:
                obj._logger.debug("Found people info section (<%s>)", CommonSection.People.TAG_STR)
                obj.people = CommonSection.People.from_xml_element(e)

            else:
                obj._logger.warning("Ignoring unknown section <%s>" % (e.tag))
                pass # Ignored tag

        obj._logger.debug("Created from XML : %s" % (repr(obj)))

        return obj

    def get_constants_snippet_filename(self,
                                       i_root_folder     : Optional[Union[str,
                                                                    Path]] = Path(),
                                       i_fallback_format : Optional[str] = None):
        assert isinstance(i_root_folder,     str) or \
               isinstance(i_root_folder,     Path)
        assert isinstance(i_fallback_format, str) or i_fallback_format is None

        if      self.constants_file_format is not None:
            format_str = self.constants_file_format
        elif    i_fallback_format is not None:
            format_str = i_fallback_format
        else:
            raise Exception("No format given")

        return Path(i_root_folder).joinpath(format_str.format())

    def __str__(self):
        return "'%s' - '%s' [%s]" % (str(self.project), str(self.title), str(self.people))

    def __repr__(self):
        return "'%s' - '%s' [%s]" % (repr(self.project), repr(self.title), repr(self.people))
