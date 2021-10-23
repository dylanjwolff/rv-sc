import os
import subprocess
import sys
import getopt
import argparse
import subprocess as sp
from solcx import install_solc

# Note the static binaries are Linux only, so OK to assume /'s for paths
INSTALL_DIR = os.path.expanduser("~/.solcx")
SOLC_VERSIONS = open(
    os.path.expanduser("config/solc-versions.txt")).readlines()


def vtuple(v):
    s = v.split(".")
    return (s[0][1:], s[1], s[2])


def major(v):
    return vtuple(v)[1]


class Solc:
    def __init__(self, v: str, use_mm=False):
        v = v.strip()
        assert v[0].isdigit() or v[0] == '^'
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

    def can_nonbreaking_upgrade_by(self, v):
        bytuple = vtuple(v)
        mytuple = vtuple(self.version)

        if mytuple[0] != bytuple[0] or mytuple[1] != bytuple[1]:
            return False

        if int(mytuple[2]) < int(bytuple[2]):
            return True
        else:
            return False

    def find_major_match(self, vers):
        vers = sorted(vers)
        vers.reverse()
        for v in vers:
            if self.can_nonbreaking_upgrade_by(v):
                return v.strip()
        return self.version

    def get(self):
        if self.use_mm:
            return self.mm
        else:
            return self.version

    def install(self):
        v = self.get()
        if not v in available():
            install_solc(v)


def available():
    fnames = os.listdir(INSTALL_DIR)
    vs = [fname.split("-v")[1] for fname in fnames]
    return vs


print(Solc("^0.4.18").get())