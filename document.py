#! python3
import  os
import  xml.etree.ElementTree   as ETree
from    requirements_set        import RequirementsSet
from    common_section          import CommonSection
from    generator               import Generator

class Document:

    def __init__(self):
        self.common = None
        self.reqs   = None

    @classmethod
    def from_xml(cls,
                 i_tree : ETree.ElementTree):
        assert isinstance(i_tree, ETree.ElementTree)

        root = i_tree.getroot()

        # Normalize (lowercase) the XML file tags and attributes
        Document._normalize_tags(root)
        Document._normalize_attr(root)

        obj = cls()

        # Search for common section
        for base in root:
            if      base.tag == CommonSection.COMMON_TAG_STR:
                assert obj.common is None
                obj.common = CommonSection.from_xml_element(i_elt = base)
            else:
                pass

        assert obj.common is not None

        # Search for requirements section
        for base in root:
            if      base.tag == RequirementsSet.REQ_SET_TAG_STR:
                assert obj.reqs is None
                obj.reqs = RequirementsSet.from_xml_element(i_elt    = base,
                                                            i_common = obj.common)
            else:
                pass

        assert obj.reqs is not None

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

    def generate_snippets(self,
                          i_root_folder : str,
                          i_generator   : Generator):
        assert isinstance(i_root_folder, str)
        assert isinstance(i_generator,   Generator)

        os.makedirs(i_root_folder, exist_ok = True)

        for _, req in self.reqs.reqs.items():
            req.generate(i_file_generator = i_generator,
                         i_root_folder    = i_root_folder)



    def __str__(self):
        return "%s\n%s\n" % (str(self.common), str(self.reqs))

    def __repr__(self):
        return "%s\n%s\n" % (repr(self.common), repr(self.reqs))
