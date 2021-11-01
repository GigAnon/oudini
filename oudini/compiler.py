#! python3
import  logging
from    document        import Document

from    pathlib         import Path
from    typing          import Optional
from    typing          import Union


class Compiler:
    def __init__(self):
        self._logger = logging.getLogger("%s-%s" %(__name__, type(self).__name__))

    def run(self,
            i_doc_root_dir: Union[str, Path],
            i_output_dir  : Union[str, Path],
            i_document    : Optional[Document]) -> None:
        raise NotImplementedError()
