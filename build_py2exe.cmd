@echo off
title build_py2exe.cmd

rem Requires python 3.4 since that's as high as py2exe supports!
py -3.4 -m py2exe.build_exe -d . -b 0 pop\__main__.py

pause
