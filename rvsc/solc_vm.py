import os
import subprocess
import sys
import getopt
import argparse
import subprocess as sp

# Note the static binaries are Linux only, so OK to assume /'s for paths
INSTALL_DIR = os.path.expanduser("~/.solc-vm")
os.system(f"mkdir -p {INSTALL_DIR}")
SOLC_VERSIONS = open(
    os.path.expanduser("config/solc-versions.txt")).readlines()


def vtuple(v):
    s = v.split(".")
    return (s[0][1:], s[1], s[2])


def major(v):
    return vtuple(v)[1]


class Solc:
    def __init__(self, v: str, major=False, use_major_match=False):
        v = v.strip()
        v = v[1:]
        v = "v" + v
        fname = f"solc-{v}"
        self.fname = fname
        self.version = v
        self.major_match = self.find_major_match(available())
        self.mm_fname = f"solc-{self.major_match}"
        self.use_major_match = use_major_match

        if major:
            v = self.find_major_match(vers=SOLC_VERSIONS)
            self.use_major_match = True
            self.major_match = v
            self.mm_fname = f"solc-{v}"

        if self.use_major_match:
            v = self.major_match
            fname = self.mm_fname
        else:
            v = self.version
            fname = self.fname

        os.system(f"mkdir -p {INSTALL_DIR}")
        if not os.path.exists(f"{INSTALL_DIR}/{fname}"):
            print("?")
            os.system(
                f"wget https://github.com/ethereum/solidity/releases/download/{v}/solc-static-linux"
            )
            os.system(f"mv solc-static-linux {INSTALL_DIR}/{fname}")
            os.system(f"chmod u+x {INSTALL_DIR}/{fname}")

    def exec(self, f):
        if not self.use_major_match:
            fname = self.fname
        else:
            fname = self.mm_fname
        return sp.run([f"{INSTALL_DIR}/{fname}", f], capture_output=True)

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


def available():
    fnames = os.listdir(INSTALL_DIR)
    vs = [fname.split("-")[1] for fname in fnames]
    return vs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-M', '--major', action='store_true')
    parser.add_argument('-m', '--use-major-match', action='store_true')
    parser.add_argument('versions', nargs='*')
    args = parser.parse_args()

    for v in args.versions:
        sc = Solc(v, major=args.major, use_major_match=args.use_major_match)
        if sc.use_major_match:
            print(f"Installed solc-{sc.find_major_match(available())}")
        else:
            print(f"Installed solc-{sc.version}")
