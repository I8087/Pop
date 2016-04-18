@echo off
title run.cmd
cd build
echo Running test1...
test1.exe
echo test1 error level is %errorlevel%.
echo Running test2...
test2.exe
echo test1 error level is %errorlevel%.
echo All done with the tests!
pause
