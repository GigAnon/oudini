#! python3

import  xml.etree.ElementTree   as ElementTree
from    document                import Document
from    latex_generator         import LatexGenerator
from    miktex_compiler         import MiktexCompiler

import  logging
import  os
from    pathlib                 import Path

from timeit import default_timer as timer


# Setup logging system
# FORMAT = "[%(name)-30s][%(asctime)s][%(levelname)-8s][%(filename)25s:%(lineno)-4s %(funcName)-25s] %(message)s"
FORMAT = "[%(asctime)s][%(levelname)-8s][%(filename)25s:%(lineno)-4s %(funcName)-25s] %(message)s"
logging.basicConfig(format  = FORMAT,
                    datefmt = "%H:%M:%S",
                    level   = logging.INFO)

logging.getLogger("envutils").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

PROJECT_ROOT_DIR = Path(r"D:/DataDump/OuDini/demo/project1/").resolve()

doc = Document.from_xml(ElementTree.parse(os.path.join(PROJECT_ROOT_DIR, "SP-SRD-COMP1.xml")))

compiler = MiktexCompiler(i_miktex_bin_dir = Path("E:/miktex-portable/texmfs/install/miktex/bin/x64"))

latex_generator = LatexGenerator(i_document         = doc,
                                 i_project_root_dir = PROJECT_ROOT_DIR,
                                 i_compiler         = compiler)


start_time = timer()

latex_generator.generate_and_compile(i_out_dir = PROJECT_ROOT_DIR.joinpath('out'))

end_time = timer()

logger.info("Elapsed time: %f s" % (end_time - start_time))