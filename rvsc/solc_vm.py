"""Solidity Version Manager
"""
import os
import sys
from solcx import install_solc

# Note the static binaries are Linux only, so OK to assume /'s for paths
INSTALL_DIR = os.path.expanduser("~/.solcx")
SOLC_VERSIONS = open(
    os.path.expanduser("config/solc-versions.txt")).readlines()


def vtuple(ver):
    s = ver.split(".")
    return (s[0][1:], s[1], s[2])


def major(ver):
    return vtuple(ver)[1]


class Solc:
    """Class for finding appropriate versions of Solc to use from a base version
    """
    def __init__(self, v: str, use_mm=False, force_exact=False):
        assert not (force_exact and use_mm)
        v = v.strip()
        assert v[0].isdigit() or v[0] == "^"
        if v[0] == "^":
            self.version = v[1:]
            self.use_mm = True
        else:
            self.version = v
            self.use_mm = use_mm
        local = self.find_major_match(available())
        remote = self.find_major_match(SOLC_VERSIONS)
        if not self.can_nonbreaking_upgrade_by(local):
            self.mm = remote
        else:
            self.mm = local

        if force_exact:
            self.use_mm = False

    def can_nonbreaking_upgrade_by(self, v):
        """Determine if self.version can be safely upgraded by v

        Args:
            v (str): a version string

        Returns:
            bool: True iff upgradeable
        """
        bytuple = vtuple(v)
        mytuple = vtuple(self.version)

        if mytuple[0] != bytuple[0] or mytuple[1] != bytuple[1]:
            return False

        if int(mytuple[2]) < int(bytuple[2]):
            return True
        else:
            return False

    def find_major_match(self, vers):
        """finds a major version (release.major.minor) match in vers for self.version

        Args:
            vers ([str]): a list of candidate version strings

        Returns:
            str: the matching version string (or self.version if no match)
        """
        vers = sorted(vers)
        vers.reverse()
        for v in vers:
            if self.can_nonbreaking_upgrade_by(v):
                return v.strip()
        return self.version

    def get(self):
        """Gets the version (or its major match if self.use_mm )

        Returns:
            str: the version string
        """
        if self.use_mm:
            return self.mm
        else:
            return self.version

    def install(self):
        """Installs the appropriate version of Solc with Solcx
        """
        v = self.get()
        if not v in available():
            install_solc(v)


def available():
    """lists already installed versions of the Solidity compiler 

    Returns:
        [str]: a list of version strings
    """
    fnames = os.listdir(INSTALL_DIR)
    vs = [fname.split("-v")[1] for fname in fnames]
    return vs


if __name__ == "__main__":
    v = sys.argv[1]
    Solc(v).install()
