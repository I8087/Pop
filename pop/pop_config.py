import os
import sys
import platform


class Config():
    """This class returns build values based on platform values."""

    def config(self, sysplatform=""):

        # Setup the platform default options.
        options = {"platform": sys.platform,
                   "machine": platform.machine(),
                   "system": platform.system(),
                   "BIT": 32  # Legacy code!!!
                   }

        # Allow the platform to be overridable.
        if sysplatform:
            options["platform"] = sysplatform

        return options
