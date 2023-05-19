"""
Script to convert mmCIF files to PDB format.
usage: python cif2pdb.py ciffile [pdbfile]
Requires python BioPython (`pip install biopython`). It should work with recent version of python 2 or 3.
@author Spencer Bliven <spencer.bliven@gmail.com>
"""

import sys
import argparse
import logging
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB import PDBIO

from molecular_converter.exceptions import OutOfChainsError
from molecular_converter.utils import int_to_chain, rename_chains


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert mmCIF to PDB format')
    parser.add_argument("ciffile",help="mmCIF input file")
    parser.add_argument("pdbfile",nargs="?",help="PDB output file. Default based on CIF filename")
    parser.add_argument("-v","--verbose", help="Long messages",
        dest="verbose",default=False, action="store_true")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG if args.verbose else logging.WARN)

    ciffile = args.ciffile
    pdbfile = args.pdbfile or ciffile+".pdb"
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

    if args.verbose:
        for new,old in chainmap.items():
            if new != old:
                logging.info("Renaming chain {0} to {1}".format(old,new))

    #Write PDB
    io = PDBIO()
    io.set_structure(structure)
    io.save(pdbfile)
