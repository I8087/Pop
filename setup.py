from distutils.core import setup
import py2exe
import sys

# This is a standalone script, let it fill in the parameters.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")

setup(
    name = "pop",
    description = "The pop compiler.",
    version = "0.1.1",
    zipfile = None,
    options = {
        "py2exe": {
            "compressed": True,
            "optimize": 2,
            "dist_dir": ".",
            "bundle_files": 1
            }
        },

    console = [
        {
            "script": "pop/__main__.py",
            "icon_resources": [(0, "pop.ico")],
            "dest_base": "pop"
        }
    ]
    )
