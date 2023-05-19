"""
CLI to convert mmCIF files to PDB format.

Usage:
    $ molconverter cif_file [pdb_file] [--verbose]
"""

import sys
import argparse
import logging
from typing_extensions import Annotated

from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB import PDBIO
import typer

from molecular_converter.exceptions import OutOfChainsError
from molecular_converter.utils import int_to_chain, rename_chains

app = typer.Typer()

@app.command("mmcif_to_pdb")
def mmcif_to_pdb(cif_file: str, pdb_file: str = None, verbose: bool = False):
    """
    Convert mmCIF to PDB format.

    Parameters
    ----------
    ciffile : str
        Path to mmCIF input file.
    pdbfile : str
        Path to PDB output file. Default is `{cif_file}.pdb`.
    verbose : bool
        Verbose output.
    """
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG if verbose else logging.WARN)

    ciffile = cif_file
    pdbfile = pdb_file or ciffile+".pdb"
    #Not sure why biopython needs this to read a cif file
    strucid = ciffile[:4] if len(ciffile)>4 else "1xxx"

    # Read file
    parser = MMCIFParser()
    structure = parser.get_structure(strucid, ciffile)

    # rename long chains
    try:
        chainmap = rename_chains(structure)
    except OutOfChainsError:
        logging.error("Too many chains to represent in PDB format")
        sys.exit(1)

    if verbose:
        for new,old in chainmap.items():
            if new != old:
                logging.info("Renaming chain {0} to {1}".format(old,new))

    #Write PDB
    io = PDBIO()
    io.set_structure(structure)
    io.save(pdbfile)


def main():
    """
    Main entrypoint for the CLI.
    """
    app()
