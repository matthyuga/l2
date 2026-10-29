@echo off
setlocal
set "PATH=E:\l2-local\tools\node-v24.22.0-win-x64;%PATH%"
set "GHIDRA_INSTALL_DIR=E:\l2-local\tools\ghidra_12.1.4_PUBLIC"
set "JAVA_HOME=E:\l2-local\tools\jdk-25.0.4.1+1"
set "REA_ANALYSIS_PROVIDER=ghidra"
"E:\l2-local\tools\node-v24.22.0-win-x64\node.exe" "E:\l2-local\tools\rea-runtime\node_modules\rea-agents\scripts\rea.mjs" %*
