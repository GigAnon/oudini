#! python3

import  xml.etree.ElementTree   as ElementTree
from    document                import Document
from    latex_generator         import LatexGenerator

doc = Document.from_xml(ElementTree.parse("test.xml"))

print(repr(doc))

doc.generate_snippets("TexTest/src/snip/",
                      i_generator = LatexGenerator())
