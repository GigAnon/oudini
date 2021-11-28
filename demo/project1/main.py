#! python3
import  logging
import  os
import  sys
import time
from    pathlib                 import Path
import  xml.etree.ElementTree   as ElementTree
from    timeit import default_timer as timer

# OuDini imports
# Note: if OuDini is installed as a package, sys.path doesn't need to be modified
sys.path.append(str(Path().joinpath('..', '..', 'oudini')))

from    document                import Document
from    latex.latex_generator   import LatexGenerator
from    latex.miktex_compiler   import MiktexCompiler

import  utils.logobj            as LogUtils


PROJECT_ROOT_DIR = Path(__file__).parent.resolve()
LOG_DIR = PROJECT_ROOT_DIR.joinpath('logs')
OUT_DIR = PROJECT_ROOT_DIR.joinpath('out')

LOG_DIR.mkdir(exist_ok = True)
OUT_DIR.mkdir(exist_ok = True)

# Setup logging system
LogUtils.simple_setup(handlers =
                      [ logging.StreamHandler(),
                        (logging.FileHandler(filename = f"{LOG_DIR}/test.log",
                                             mode     = "w"),
                         logging.NOTSET,
                         logging.Formatter(fmt     = "[%(name)-35s][%(asctime)s][%(levelname)-8s][%(filename)25s:%(lineno)-4s %(funcName)-25s] %(message)s",
                                           datefmt = "%H:%M:%S"))
                      ])

logging.getLogger("envutils").setLevel(logging.WARNING)
#########


logger = logging.getLogger(__name__)
logger.warning(f"{'*'*5} Running script: {Path(__file__).parent.resolve()} {'*'*5}")

doc = Document.from_xml(ElementTree.parse(os.path.join(PROJECT_ROOT_DIR, "SP-SRD-COMP1.xml")))

compiler = MiktexCompiler(i_miktex_bin_dir = Path("E:/miktex-portable/texmfs/install/miktex/bin/x64"))

latex_generator = LatexGenerator(i_project_root_dir = PROJECT_ROOT_DIR,
                                 i_compiler         = compiler)


start_time = timer()

latex_generator.generate_and_compile(i_document = doc,
                                     i_out_dir  = OUT_DIR)

end_time = timer()

logger.info("Elapsed time: %f s" % (end_time - start_time))
