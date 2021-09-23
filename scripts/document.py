#! python3
import  logging
import  xml.etree.ElementTree   as ETree
from    requirements_set        import RequirementsSet
from    common_section          import CommonSection
from    glossary                import Glossary


class Document:

    def __init__(self,
                 i_glossary_class       : Glossary        = Glossary,
                 i_common_section_class : CommonSection   = CommonSection,
                 i_req_set_class        : RequirementsSet = RequirementsSet):
        self._logger = logging.getLogger("%s-%s" %(__name__, type(self).__name__))
        self.root_name  = "document"

        self.common     = None
        self.reqs       = None
        self.glossary   = None

        self._glossary_class        = i_glossary_class
        self._common_section_class  = i_common_section_class
        self._req_set_class         = i_req_set_class

    def to_xml(self) -> ETree.ElementTree:
        self._logger.info(f"Generating XML for document {repr(self.common.title)}")

        assert (self.common is not None)
        assert (self.reqs   is not None)

        root = ETree.Element(self.root_name)

        self._logger.debug("Generating XML for common section")
        root.append(self.common.to_xml())

        if self.glossary is not None:
            self._logger.debug("Generating XML for glossary section")
            root.append(self.glossary.to_xml())

        self._logger.debug("Generating XML for requirements section")
        root.append(self.reqs.to_xml())

        ETree.indent(root, space = ' '*4)
        return ETree.ElementTree(root)

    @classmethod
    def from_xml(cls,
                 i_tree : ETree.ElementTree):
        """
        Generates a Document object from an XML structure

        :param i_tree: Root of the XML document to parse
        :return      : Created Document object created from the XML
        """
        assert isinstance(i_tree, ETree.ElementTree)

        root = i_tree.getroot()

        # Normalize (lowercase) the XML file tags and attributes
        Document._normalize_tags(root)
        Document._normalize_attr(root)

        obj = cls()

        obj._logger.info("Creating document from XML")

        # Read root tag name
        obj.root_name = root.tag

        # Search for common section and glossary
        for base in root:
            if      base.tag == obj._common_section_class.TAG_STR:
                obj._logger.debug(f"Found common section (<{base.tag}>, class '{obj._common_section_class.__name__}')")

                assert obj.common is None
                obj.common = obj._common_section_class.from_xml_element(i_elt = base)

            elif    base.tag == obj._glossary_class.TAG_STR:
                obj._logger.debug(f"Found glossary section (<{base.tag}>, class '{obj._glossary_class.__name__}')")

                assert obj.glossary is None
                obj.glossary = obj._glossary_class.from_xml_element(i_elt = base)

            else:
                pass

        # Common section is not optional
        assert obj.common is not None
        # Glossary is optional

        # Search for requirements section
        for base in root:
            if      base.tag == obj._req_set_class.TAG_STR:
                obj._logger.debug(f"Found requirements section (<{base.tag}>, class '{obj._req_set_class.__name__}')")
                assert obj.reqs is None
                obj.reqs = obj._req_set_class.from_xml_element(i_elt    = base,
                                                               i_common = obj.common)

            else:
                pass

        # Requirements section is not optional
        assert obj.reqs is not None

        obj._logger.info("Document [{project}:{document}] successfully parsed ({num_req} requirements found)".format(project  = repr(obj.common.project),
                                                                                                                     document = repr(obj.common.title),
                                                                                                                     num_req  = len(obj.reqs.reqs)))
        obj._logger.debug(repr(obj))

        return obj

    @staticmethod
    def _normalize_tags(i_root):
        i_root.tag = i_root.tag.lower()
        for child in i_root:
            Document._normalize_tags(child)

    @staticmethod
    def _normalize_attr(i_root):
        for attr in list(i_root.attrib):
            norm_attr = attr.lower()
            if norm_attr != attr:
                i_root.set(norm_attr, i_root.attrib[attr])
                i_root.attrib.pop(attr)

        for child in i_root:
            Document._normalize_attr(child)

    def __str__(self):
        s = "%s\n%s\n" % (str(self.common), str(self.reqs))

        if self.glossary:
            s += "%s" % (str(self.glossary))

        return s

    def __repr__(self):
        s = "%s\n%s\n" % (repr(self.common), repr(self.reqs))

        if self.glossary:
            s += "%s" % (repr(self.glossary))

        return s
