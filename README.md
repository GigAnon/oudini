# Quick install / setup

## LaTeX generation demo

- [WIP] Install a LaTeX generator (ATM MikTeX + pdflatex is supported)

- Download the repository
- Open the demo project in demo/project1 folder
- [WIP] in main.py, edit the path to your LaTeX generator
- Run main.py

Note: if using MikTeX, additionnal LaTeX packages will have to be installed. [WIP] ATM MikTeX installer is disabled when running the MiktexCompiler class - run the pdflatex command without the -disable-installer option.


# OuDini
## What is OuDini ?

OuDini is a Python framework designed to allow a no-nonesense management of complex functionnal requirement specifications:
- Redaction
- Inter-document links (V-cycle requirements, etc.)
- Template-based document generation for the specification documents, dependency matrices, etc.
- Versioning, including baselining
- Maintenance
- [TBD] Reviews

## Why OuDini ? 

OuDini was born from the frustration created by proprietary tools such as IBM Doors. Bloated, expensive, awkward to use and difficult to extend, those tools are often a poor solution to the problems usually seen in large projects where specifications are layered into dozen of documents:
- Each specification document spans hundred of requirements
- Each document must be precisely versionned, and the differences between versions must be easily analysed
- Requirements are written by multiple authors, and must be easily merged, proof-read and reviewed
- Links between documents spans in the thousands. Tracability must be guaranteed - including links that are missing, obsolete, useless (one-to-many and many-to-one)...
- Document generation must be reasonably fast, reproductible, easily maintained, and template based
- Documents must be accessible concurently without network access, license limitations (be them concurent users or a date), from any modern OS

Furthermore, because each project has specific needs, the database and its tools must be easily extendable to add custom functionalities. For instance, the tools must be able to interact with both testing / validation frameworks (in Python, etc.), CI automation systems (Jenkins, etc.), code generation (protocol requirements in ASN.1, etc.), audit tools, spreadsheet applications (Excel, CSVs, etc.), and so on.

I mean, how hard can it possibly be?

Thus, several criteria were specifically outlined that a proof of concept - that is, OuDini - should have:
- Open source with a truly free license (MIT)
  - Just use it. No licensing servers nonesense. 
- Developed as a modern Python 3 package
  - Ease of extension by any developer (because whatever they need to do, there's a module for that)
  - Can run on any system with a Python interpreter
  - Lightweight
- Uses a XML-based file database
  - Human searchable, readable and writable
  - Easily parsed by third-party applications, or maintenance scripts
  - Works nicely with CVS such as Git
- Generic generation / rendering engine
  - By default, a LaTeX generator is provided
- Multi-documents interactions
  - Links, matrices, etc.

Hence, OuDini was born.
