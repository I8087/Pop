## [Unreleased]
### Added
- The compiler will now keep assembly files if specified.
- Structures are now supported.
- Addressing is now supported.
- Classes are now supported.
- The compiler now leaves the compiler's version in the assembly output for debugging purposes.

### Changed
- The compiler can now compile multiple files at once.
- Test files will be housed in ./test
- Small changes to the test build scripts. Mainly replacing batch scripts with Python scripts.
- The compiler will now generate cleaner assembly files.

### Fixed
- The extern command now works.
- Fixed a bug where any error message would crash the compiler.
- Fixed several small path bugs.
- Fixed a bug that prevented the pretty printing of assembly files.
- Fixed a pathing problem for the win32 build.
- Fixed a bug that didn't let you call a function with no parameters.

## [0.1.1] - 2016-4-11
### Added
- Added a change log.
- Added py2exe build script. It was written in batch, but is now in Python.

### Changed
- Moved main.py into pop/\_\_main\_\_.py
- Updated the release .zip file, it's now just one executable and much more user friendly!

### Removed
- Removed stub.c since the project now uses py2exe instead of cython.
- Removed the unneeded Cython build script.

## 0.1.0 - 2016-3-31
### Added
- Initial release committed.

[Unreleased]: https://github.com/I8087/Pop/compare/v0.1.1...master
[0.1.1]: https://github.com/I8087/Pop/compare/v0.1...v0.1.1
