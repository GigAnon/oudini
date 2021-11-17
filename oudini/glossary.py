#! python3
from    utils.logobj            import LogObj
import  xml.etree.ElementTree   as ETree


class Glossary (LogObj):
    TAG_STR = "glossary"

    class Definition (LogObj):
        TAG_STR        = "definition"
        ATTR_UID       = "uid"

        def __init__(self):
            LogObj.__init__(self)
            self.uid         = None
            self.description = None

        @classmethod
        def from_xml_element(cls,
                             i_elt    : ETree.Element):
            assert isinstance(i_elt, ETree.Element)
            assert i_elt.tag == cls.TAG_STR

            obj = cls()
            obj._logger.debug(f"Creating '{cls.__name__}' {obj.uid} from XML")

            obj.uid         = i_elt.get(cls.ATTR_UID)
            obj.description = i_elt.text

            assert obj.description  is not None
            assert obj.uid          is not None

            return obj

        def __str__(self):
            return self.uid

        def __repr__(self):
            return f"'{self.uid}': '{self.description}'"

    class Acronym (Definition):
        TAG_STR        = "acronym"
        ATTR_SHORTHAND = "shorthand"

        def __init__(self):
            self.shorthand = None
            super().__init__()

        @classmethod
        def from_xml_element(cls,
                             i_elt    : ETree.Element):
            obj = super().from_xml_element(i_elt)

            obj.shorthand = i_elt.get(cls.ATTR_SHORTHAND)
            # Note: shorthand may be None
            return obj

        def __repr__(self):
            return f"'{self.uid}' ['{self.shorthand or self.uid}']: '{self.description}'"

    _sub_types = [ Acronym, Definition ]

    def __init__(self):
        LogObj.__init__(self)
        self.definitions = {}

    def to_xml(self) -> ETree.Element:
        root = ETree.Element(self.TAG_STR)

        root.text = ' ' # To prevent the generator from generating an empty tag <glossary />

        self._logger.warning("Not implemented")
        return root

    @classmethod
    def from_xml_element(cls,
                         i_elt    : ETree.Element):
        assert isinstance(i_elt,    ETree.Element)
        assert i_elt.tag == cls.TAG_STR

        obj = cls()

        for e in i_elt:
            class_ctor = None
            for def_type in cls._sub_types:
                if e.tag == def_type.TAG_STR:
                    class_ctor = def_type

            if class_ctor is not None:
                definition = class_ctor.from_xml_element(e)
                obj.definitions[definition.uid] = definition
            else:
                obj._logger.warning(f"Ignoring unknown section <{e.tag}>")

        obj._logger.info(f"Created glossary ({len(obj.definitions)} definitions) from XML")
        return obj

    def __str__(self):
        return f"{self.definitions!s}"

    def __repr__(self):
        return f"{self.definitions!r}"

    def __iter__(self):
        return iter(self.definitions.items())
