REM @echo off
setlocal

set SCRIPT_DIR=%~dp0

set MIKTEX_PATH="E:/miktex-portable/texmfs/install/miktex/bin/x64"
set PATH=%MIKTEX_PATH%;%PATH%

set DOC_NAME=main
set OUT_DIR=%SCRIPT_DIR%/../out
set OUT_TMP_DIR=%OUT_DIR%/tmp

set PDFLATEX_CMD=pdflatex.exe -disable-installer -halt-on-error -interaction=nonstopmode -output-directory=%OUT_TMP_DIR% %DOC_NAME%.tex

REM pdflatex.exe --help
REM makeglossaries-lite.exe --help
%PDFLATEX_CMD%
cd %OUT_TMP_DIR%
makeglossaries-lite.exe %DOC_NAME% -t makeglossaries-lite.log
cd %SCRIPT_DIR%
%PDFLATEX_CMD%
%PDFLATEX_CMD%

copy "%OUT_TMP_DIR%/%DOC_NAME%.pdf" "%OUT_DIR%/%DOC_NAME%.pdf"
