#! python3
from    utils.logobj    import LogObj
from    document        import Document

from    pathlib         import Path
from    typing          import Optional
from    typing          import Union


class Compiler (LogObj):
    """
        Abstract interface for a OuDini compiler class.
    """
    def __init__(self):
        """
            Constructor
        """
        LogObj.__init__(self)

    def run(self,
            i_doc_root_dir: Union[str, Path],
            i_output_dir  : Union[str, Path],
            i_document    : Optional[Document]) -> None:
        """
            TODO
        :param i_doc_root_dir   : TODO
        :param i_output_dir     : TODO
        :param i_document       : TODO
        """
        raise NotImplementedError()
