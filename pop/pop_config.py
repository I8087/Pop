import os, sys, platform


class Config():
    """This class returns build values based on platform values."""

    def config(self, sysplatform=""):

        # Setup the platform default options.
        options = {"platform": sys.platform,
                   "machine": platform.machine,
                   "system": platform.system
                   }

        # Allow the platform to be overridable.
        if sysplatform:
            options["platform"] = sysplatform

        return options
