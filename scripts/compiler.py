#! python3

from    document        import Document

from    pathlib         import Path
from    typing          import Optional
from    typing          import Union


class Compiler:
    def __init__(self):
        pass

    def run(self,
            i_doc_root_dir: Union[str, Path],
            i_output_dir  : Union[str, Path],
            i_document    : Optional[Document] = None) -> None:
        raise NotImplementedError()
