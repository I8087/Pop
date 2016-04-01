rem requires mingw and python 3.4.2!
@echo off
title build.cmd
cython --embed -o pop.c main.py
c:\mingw\bin\gcc.exe -I"c:\Program Files\python34\include" -L"c:\Program Files\python34\libs" pop.c stub.c -opop.exe -lpython34
pause