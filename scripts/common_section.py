#! python3
import  logging
import  xml.etree.ElementTree   as ETree
from    typing                  import Optional
from    typing                  import Union
from    pathlib                 import Path


class CommonSection:
    COMMON_TAG_STR              = "general"
    REQDISPLAYFORMAT_TAG_STR    = "reqdisplayformat"
    REQFILEFORMAT_TAG_STR       = "reqfileformat"

    PROJECT_TAG_STR             = "project"
    PROJECT_ATTR_INTERNAL_STR   = "internal"
    PROJECT_ATTR_PRETTY_STR     = "pretty"

    TITLE_TAG_STR               = "title"
    TITLE_ATTR_INTERNAL_STR     = "internal"
    TITLE_ATTR_PRETTY_STR       = "pretty"

    PEOPLE_TAG_STR              = "people"

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

    class Title:
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

    class People:
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

            def __str__(self):
                return "'%s' ('%s')" % (self.name, self.role)

            def __repr__(self):
                return self.__str__()

        def __init__(self):
            self._logger = logging.getLogger("%s-%s" %(__name__, type(self).__name__))
            self.list = []

        @classmethod
        def from_xml_element(cls,
                             i_elt : ETree.Element):
            assert isinstance(i_elt, ETree.Element)
            assert i_elt.tag == CommonSection.PEOPLE_TAG_STR

            obj = cls()

            for e in i_elt:
                if      e.tag == CommonSection.People.PERSON_TAG_STR:
                    obj.list.append(CommonSection.People.Elt(i_name = e.text.strip(),
                                                             i_role = e.get(CommonSection.People.PERSON_ATTR_ROLE_STR).strip()))
                    obj._logger.debug("Section (<%s>) : '%s' ('%s')", CommonSection.People.PERSON_TAG_STR,
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
        self._logger = logging.getLogger("%s-%s" %(__name__, type(self).__name__))

        self.project                = None
        self.title                  = None
        self.people                 = None
        self.req_display_format     = None
        self.req_file_format        = None
        self.constants_file_format  = None

    @classmethod
    def from_xml_element(cls,
                         i_elt : ETree.Element):
        assert isinstance(i_elt, ETree.Element)
        assert i_elt.tag == CommonSection.COMMON_TAG_STR

        obj = cls()

        for e in i_elt:
            if      e.tag == CommonSection.REQDISPLAYFORMAT_TAG_STR:
                obj._logger.debug("Found requirement display format section (<%s>)", CommonSection.REQDISPLAYFORMAT_TAG_STR)
                obj.req_display_format = e.text

            elif    e.tag == CommonSection.REQFILEFORMAT_TAG_STR:
                obj._logger.debug("Found requirement file format section (<%s>)", CommonSection.REQFILEFORMAT_TAG_STR)
                obj.req_file_format = e.text

            elif    e.tag == CommonSection.PROJECT_TAG_STR:
                obj._logger.debug("Found project info section (<%s>)", CommonSection.PROJECT_TAG_STR)
                obj.project = CommonSection.Project(i_internal_name = e.get(CommonSection.PROJECT_ATTR_INTERNAL_STR),
                                                    i_pretty_name   = e.get(CommonSection.PROJECT_ATTR_PRETTY_STR))
                obj._logger.debug(repr(obj.project))

            elif    e.tag == CommonSection.TITLE_TAG_STR:
                obj._logger.debug("Found document title info section (<%s>)", CommonSection.TITLE_TAG_STR)
                obj.title = CommonSection.Title(i_internal_name = e.get(CommonSection.TITLE_ATTR_INTERNAL_STR),
                                                i_pretty_name   = e.get(CommonSection.TITLE_ATTR_PRETTY_STR))
                obj._logger.debug(repr(obj.title))

            elif    e.tag == CommonSection.PEOPLE_TAG_STR:
                obj._logger.debug("Found people info section (<%s>)", CommonSection.PEOPLE_TAG_STR)
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
