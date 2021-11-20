#! python3
from    utils.logobj            import LogObj
import  xml.etree.ElementTree   as ETree
from    typing                  import Optional
from    typing                  import Union
from    pathlib                 import Path


class CommonSection (LogObj):
    """
        Class for manipulation of the common section of an Oudini document.
        This section contains data that is typically relevant to the document as a whole, or to all requirements:
            - Project name and unique identifier
            - Document name and unique identifier
            - Authors
            - Formating templates
            - Etc.
    """
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

    class People (LogObj):
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
            LogObj.__init__(self)
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
                    obj._logger.warning(f"Ignoring unknown section <{e.tag}>")
                    pass # Ignored tag

            obj._logger.debug(f"Created from XML : {repr(obj)}")

            return obj

        def __str__(self):
            return str(self.list)

        def __repr__(self):
            return repr(self.list)

    def __init__(self):
        LogObj.__init__(self)

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

        if self.req_display_format:
            ETree.SubElement(root,
                             self.REQDISPLAYFORMAT_TAG_STR).text = self.req_display_format

        if self.req_file_format:
            ETree.SubElement(root,
                             self.REQFILEFORMAT_TAG_STR).text = self.req_file_format

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
                obj._logger.debug(f"Found requirement display format section (<{cls.REQDISPLAYFORMAT_TAG_STR}>)")
                obj.req_display_format = e.text

            elif    e.tag == cls.REQFILEFORMAT_TAG_STR:
                obj._logger.debug(f"Found requirement file format section (<{cls.REQFILEFORMAT_TAG_STR}>)")
                obj.req_file_format = e.text

            elif    e.tag == cls.Project.TAG_STR:
                obj._logger.debug(f"Found project info section (<{cls.Project.TAG_STR}>)")
                obj.project = cls.Project.from_xml_element(e)
                obj._logger.debug(repr(obj.project))

            elif    e.tag == cls.Title.TAG_STR:
                obj._logger.debug(f"Found document title info section (<{cls.Title.TAG_STR}>)")
                obj.title = cls.Title.from_xml_element(e)
                obj._logger.debug(repr(obj.title))

            elif    e.tag == cls.People.TAG_STR:
                obj._logger.debug(f"Found people info section (<{cls.People.TAG_STR}>)")
                obj.people = cls.People.from_xml_element(e)

            else:
                obj._logger.warning(f"Ignoring unknown section <{e.tag}>")
                pass # Ignored tag

        obj._logger.debug(f"Created from XML : {obj!r}")

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
        return f"'{self.project!s}' - '{self.title!s}' [{self.people!s}]"

    def __repr__(self):
        return f"'{self.project!r}' - '{self.title!r}' [{self.people!r}]"
