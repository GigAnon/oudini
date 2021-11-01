#! python3
import  logging
import  os
from    typing              import Optional
from    typing              import Union
from    pathlib             import Path

from    compiler            import Compiler
from    requirement         import Requirement
from    common_section      import CommonSection
from    glossary            import Glossary
from    document            import Document


class Generator:
    """
        Parent class for render-code snippet generation from requirements, common sections, glossaries, etc.
        This class must be derived for specific rendering solutions (i.e. LaTeX, HTML, OpenXML...).
    """
    DEFAULT_REQ_FILE_FORMAT       = "{id:05d}.txt"
    DEFAULT_CONSTANTS_FILE_FORMAT = "constants.txt"
    DEFAULT_GLOSSARY_FILE_FORMAT  = "glossary.txt"

    def __init__(self,
                 i_project_root_dir : Union[str,
                                            Path] = Path(),
                 i_compiler         : Optional[Compiler] = None):
        """
        Constructor

        :param i_project_root_dir: Root folder of the project (where to find templates, generate output files, etc.)
        :param i_compiler        : Compiler for the final document from the templates and the snippers
        """
        assert isinstance(i_project_root_dir, (str, Path))
        assert isinstance(i_compiler, Compiler) or i_compiler is None

        self._logger  = logging.getLogger("%s-%s" %(__name__, type(self).__name__))
        self.root_dir = Path(i_project_root_dir).resolve()
        # self.document = i_document # Reference, not a copy
        self.compiler = i_compiler # Reference, not a copy

    def _generate_requirement(self,
                              i_req      : Requirement,
                              i_filename : Optional[Union[str,
                                                          Path]] = None) -> str:
        """
            Internal virtual method.
            Generate snippet for requirement i_req and optionnally write it in file i_filename.
        :param i_req     : Requirement to process
        :param i_filename: Filename where to write the snippet (optionnal)
        :return          : Generated snippet code
        """
        raise NotImplementedError()


    def _generate_constants(self,
                            i_common   : CommonSection,
                            i_filename : Optional[Union[str,
                                                        Path]] = None) -> str:
        """
            Internal virtual method.
            Generate snippet for common section i_common and optionnaly write it in file i_filename.
        :param i_common  : Common section to process
        :param i_filename: Filename where to write the snippet (optionnal)
        :return          : Generated snippet code
        """
        raise NotImplementedError()

    def _generate_glossary(self,
                           i_glossary : Glossary,
                           i_filename : Optional[Union[str,
                                                       Path]] = None) -> str:
        """
            Internal virtual method.
            Generate snippet for glossary i_glossary and optionnaly write it in file i_filename.
        :param i_glossary: Glossary section to process
        :param i_filename: Filename where to write the snippet (optionnal)
        :return          : Generated snippet code
        """
        raise NotImplementedError()

    def generate_document(self,
                          i_document    : Document,
                          i_root_folder : Union[str, Path]) -> None:
        """
            Generate snippets from Oudini document i_document into folder i_root_folder.

        :param i_document   : Oudini document to generate the snippets from
        :param i_root_folder: Root folder where the snippets files will be generated
        :return: None
        """
        assert isinstance(i_document,    Document)
        assert isinstance(i_root_folder, (str, Path))

        # Convert i_root_folder to pathutils.Path
        if isinstance(i_root_folder, str):
            i_root_folder = Path(i_root_folder)

        self._logger.info("Generating document [{project}:{doc}] into '{root_folder}'".format(project     = repr(i_document.common.project),
                                                                                              doc         = "TODO",
                                                                                              root_folder = i_root_folder))

        # Create the output folder, if it doesn't already exist
        self._logger.debug("Deleting '%s'" % (i_root_folder))
        os.makedirs(i_root_folder, exist_ok = True)

        # Generate the requirements
        for _, req in i_document.reqs.reqs.items():
            self._logger.debug("Generating [%s]" % (str(req)))
            self._generate_requirement(i_req      = req,
                                       i_filename = req.get_snippet_filename(i_root_folder     = i_root_folder,
                                                                             i_fallback_format = self.DEFAULT_REQ_FILE_FORMAT))

        # Export the document constants
        self._logger.debug("Generating constants")
        self._generate_constants(i_common   = i_document.common,
                                 i_filename = i_document.common.get_constants_snippet_filename(i_root_folder     = i_root_folder,
                                                                                               i_fallback_format = self.DEFAULT_CONSTANTS_FILE_FORMAT))

        # If present: export the glossary
        if i_document.glossary is not None:
            self._logger.debug("Generating glossary")
            self._generate_glossary(i_glossary = i_document.glossary,
                                    i_filename = i_document.common.get_constants_snippet_filename(i_root_folder     = i_root_folder,
                                                                                                  i_fallback_format = self.DEFAULT_GLOSSARY_FILE_FORMAT))

        self._logger.info("Done generating [{project}:{doc}]".format(project = repr(i_document.common.project),
                                                                     doc     = "TODO"))

    def generate_and_compile(self,
                             i_document: Document,
                             i_out_dir : Union[str, Path]) -> None:
        """
            Generate snippets for Oudini document i_document, then run the document compiler.

        :param i_document : Oudini document for the generation and compilation
        :param i_out_dir  : Output directory
        :return: None
        """
        assert isinstance(i_out_dir, (str, Path))


        self.generate_document(i_document    = i_document,
                               i_root_folder = self.root_dir)
        self.compiler.run(i_output_dir   = i_out_dir,
                          i_document     = i_document,
                          i_doc_root_dir = self.root_dir)
