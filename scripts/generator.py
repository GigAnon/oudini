#! python3

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
    DEFAULT_REQ_FILE_FORMAT       = "{id:05d}.txt"
    DEFAULT_CONSTANTS_FILE_FORMAT = "constants.txt"
    DEFAULT_GLOSSARY_FILE_FORMAT  = "glossary.txt"

    def __init__(self,
                 i_document         : Document,
                 i_project_root_dir : Union[str,
                                            Path] = Path(),
                 i_compiler         : Optional[Compiler] = None):
        """
        Constructor

        :param i_document        : Document to generate
        :param i_project_root_dir: Root folder of the project (where to find templates, generate output files, etc.)
        :param i_compiler        : Compiler for the final document from the templates and the snippers
        """
        assert isinstance(i_document, Document)
        assert isinstance(i_project_root_dir, str) or \
               isinstance(i_project_root_dir, Path)
        assert isinstance(i_compiler, Compiler) or i_compiler is None

        self.root_dir = Path(i_project_root_dir).resolve()
        self.document = i_document # Reference, not a copy
        self.compiler = i_compiler # Reference, not a copy

    def _generate_requirement(self,
                              i_req      : Requirement,
                              i_filename : Optional[Union[str,
                                                          Path]] = None) -> str:
        raise NotImplementedError()


    def _generate_constants(self,
                            i_common   : CommonSection,
                            i_filename : Optional[Union[str,
                                                        Path]] = None) -> str:
        raise NotImplementedError()

    def _generate_glossary(self,
                           i_glossary : Glossary,
                           i_filename : Optional[Union[str,
                                                       Path]] = None) -> str:
        raise NotImplementedError()

    def generate_document(self,
                          i_document    : Document,
                          i_root_folder : Union[str, Path]):
        assert isinstance(i_document, Document)
        assert isinstance(i_root_folder, str) or\
               isinstance(i_root_folder, Path)

        # Convert i_root_folder to pathutils.Path
        if isinstance(i_root_folder, str):
            i_root_folder = Path(i_root_folder)

        # Create the output folder, if it doesn't already exist
        os.makedirs(i_root_folder, exist_ok = True)

        # Generate the requirements
        for _, req in i_document.reqs.reqs.items():
            self._generate_requirement(i_req      = req,
                                       i_filename = req.get_snippet_filename(i_root_folder     = i_root_folder,
                                                                             i_fallback_format = self.DEFAULT_REQ_FILE_FORMAT))

        # Export the document constants
        self._generate_constants(i_common   = i_document.common,
                                 i_filename = i_document.common.get_constants_snippet_filename(i_root_folder     = i_root_folder,
                                                                                               i_fallback_format = self.DEFAULT_CONSTANTS_FILE_FORMAT))

        # If present: export the glossary
        if i_document.glossary is not None:
            self._generate_glossary(i_glossary = i_document.glossary,
                                    i_filename = i_document.common.get_constants_snippet_filename(i_root_folder     = i_root_folder,
                                                                                                  i_fallback_format = self.DEFAULT_GLOSSARY_FILE_FORMAT))

    def generate_and_compile(self,
                             i_out_dir : Union[str, Path]):
        assert isinstance(i_out_dir, str)   or \
               isinstance(i_out_dir, Path)

        self.generate_document(i_document    = self.document,
                               i_root_folder = self.root_dir)
        # self.compiler.todo()