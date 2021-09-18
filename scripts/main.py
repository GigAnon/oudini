#! python3

import  xml.etree.ElementTree   as ElementTree
from    document                import Document
from    latex_generator         import LatexGenerator

project_root_dir = "D:/DataDump/OuDini/demo/project1/"

doc = Document.from_xml(ElementTree.parse(project_root_dir + "/SP-SRD-COMP1.xml"))

print(repr(doc))

doc.generate_snippets(project_root_dir + "/latex/snip/",
                      i_generator = LatexGenerator())

