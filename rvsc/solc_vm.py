import os

# Note the static binaries are Linux only, so OK to assume /'s for paths
INSTALL_DIR = os.path.expanduser("~/.solc-vm")


class Solc:
    def __init__(self, v: str):
        os.system(f"mkdir -p {INSTALL_DIR}")
        fname = f"solc-{v}"
        if not os.path.exists(f"{INSTALL_DIR}/{fname}"):
            print("?")
            os.system(
                f"wget https://github.com/ethereum/solidity/releases/download/{v}/solc-static-linux"
            )
            os.system(f"mv solc-static-linux {INSTALL_DIR}/{fname}")
            os.system(f"chmod u+x {INSTALL_DIR}/{fname}")
        self.version = v
        self.fname = fname

    def exec(self, f):
        os.system(f"{INSTALL_DIR}/{self.fname} {f}")


Solc("v0.4.26").exec("verx-benchmarks/Zilliqa/main.sol")
