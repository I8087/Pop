@echo off
rem requires mingw and python 3.4!
title build_py2exe.cmd
py -3.4 -m py2exe.build_exe pop\__main__.py
pause