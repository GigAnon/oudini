#! python3

import  xml.etree.ElementTree   as ElementTree
from    document                import Document
from    latex_generator         import LatexGenerator
from    miktex_compiler         import MiktexCompiler

import  os
from    pathlib                 import Path

from timeit import default_timer as timer

PROJECT_ROOT_DIR = Path(r"D:/DataDump/OuDini/demo/project1/").resolve()

doc = Document.from_xml(ElementTree.parse(os.path.join(PROJECT_ROOT_DIR, "SP-SRD-COMP1.xml")))

print(repr(doc))

compiler = MiktexCompiler(i_miktex_bin_dir = Path("E:/miktex-portable/texmfs/install/miktex/bin/x64"))

latex_generator = LatexGenerator(i_document         = doc,
                                 i_project_root_dir = PROJECT_ROOT_DIR,
                                 i_compiler         = compiler)


start_time = timer()

latex_generator.generate_and_compile(i_out_dir = PROJECT_ROOT_DIR.joinpath('out'))

end_time = timer()

print("Elapsed time: %f s" % (end_time - start_time))

