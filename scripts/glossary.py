#! python3
import os
import xml.etree.ElementTree as ETree
from   copy                  import deepcopy
from   typing                import Optional


class Glossary:
    GLOSSARY_TAG_STR    = "glossary"

    class Acronym:
        TAG_STR        = "acronym"
        ATTR_UID       = "uid"
        ATTR_SHORTHAND = "shorthand"

        def __init__(self):
            self.uid         = None
            self.shorthand   = None
            self.description = None

        @classmethod
        def from_xml_element(cls,
                             i_elt    : ETree.Element):
            assert isinstance(i_elt, ETree.Element)
            assert i_elt.tag == Glossary.Acronym.TAG_STR

            obj = cls()

            obj.uid         = i_elt.get(Glossary.Acronym.ATTR_UID)
            obj.shorthand   = i_elt.get(Glossary.Acronym.ATTR_SHORTHAND)
            obj.description = i_elt.text

            assert obj.description is not None
            assert obj.uid is not None

            return obj

        def __str__(self):
            return self.uid

        def __repr__(self):
            return "'%s' ['%s']: '%s'" % (self.uid, self.uid or self.uid, self.description)

    class Definition:
        TAG_STR        = "definition"
        ATTR_UID       = "uid"

        def __init__(self):
            self.uid         = None
            self.description = None

        @classmethod
        def from_xml_element(cls,
                             i_elt    : ETree.Element):
            assert isinstance(i_elt, ETree.Element)
            assert i_elt.tag == Glossary.Definition.TAG_STR

            obj = cls()

            obj.uid         = i_elt.get(Glossary.Definition.ATTR_UID)
            obj.description = i_elt.text

            assert obj.description is not None
            assert obj.uid is not None

            return obj

        def __str__(self):
            return self.uid

        def __repr__(self):
            return "'%s': '%s'" % (self.uid, self.description)

    def __init__(self):
        self.acronyms    = {}
        self.definitions = {}

    @classmethod
    def from_xml_element(cls,
                         i_elt    : ETree.Element):
        assert isinstance(i_elt,    ETree.Element)
        assert i_elt.tag == Glossary.GLOSSARY_TAG_STR

        obj = cls()

        for e in i_elt:
            if      e.tag == Glossary.Acronym.TAG_STR:
                acronym = Glossary.Acronym.from_xml_element(e)
                obj.acronyms[acronym.uid] = acronym
            elif    e.tag == Glossary.Definition.TAG_STR:
                definition = Glossary.Definition.from_xml_element(e)
                obj.definitions[definition.uid] = definition
            else:
                pass # Ignored tag
        return obj

    def __str__(self):
        return "%s %s" % (str(self.acronyms), str(self.definitions))

    def __repr__(self):
        return "%s\n%s" % (repr(self.acronyms), repr(self.definitions))
