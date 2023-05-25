"""
CLI to convert mmCIF files to PDB format.

Usage:
    $ molconverter cif_file [pdb_file] [--verbose]
"""

import sys
import argparse
import logging
from pathlib import Path
from typing_extensions import Annotated

from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB import PDBIO
from Bio.PDB.mmcifio import MMCIFIO
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
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if verbose else logging.WARN,
    )

    ciffile = cif_file
    pdbfile = pdb_file or cif_file.split(".")[0] + ".pdb"
    # Not sure why biopython needs this to read a cif file
    strucid = ciffile[:4] if len(ciffile) > 4 else "1xxx"

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
        for new, old in chainmap.items():
            if new != old:
                logging.info("Renaming chain {0} to {1}".format(old, new))

    # Write PDB
    io = PDBIO()
    io.set_structure(structure)
    io.save(pdbfile)


@app.command("multi_mmcif_to_pdb")
def multi_mmcif_to_pdb(cif_files_dir: str, out_dir: str = None, verbose: bool = False):
    """
    Convert multiple mmCIF to PDB format in one run.

    Parameters
    ----------
    dir_with_cif_files : str
        Path to directory with multiple mmCIF input files.
    out_dir : str
        Output directory for PDB files.
    verbose : bool
        Verbose output.
    """
    out_dir = out_dir or Path.cwd()
    for file in Path(cif_files_dir).iterdir():
        if file.suffix == ".cif":
            mmcif_to_pdb(
                cif_file=str(file),
                pdb_file=f"{out_dir}/{file.stem}.cif",
                verbose=verbose,
            )


@app.command("pdb_to_mmcif")
def pdb_to_mmcif(pdb_file: str, cif_file: str = None, verbose: bool = False):
    """
    Convert PDB to mmcif format.

    Parameters
    ----------
    pdb_file : str
        Path to PDB input file.
    mmcif_file : str
        Path to mmcif output file. Default is `{pdb_file}.cif`.
    verbose : bool
        Verbose output.
    """
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if verbose else logging.WARN,
    )

    pdbfile = pdb_file
    ciffile = cif_file or pdb_file.split(".")[0] + ".cif"
    # Not sure why biopython needs this to read a cif file
    strucid = pdbfile[:4] if len(pdbfile) > 4 else "1xxx"

    # Read file
    parser = PDBParser()
    structure = parser.get_structure(strucid, pdbfile)

    # Write mmcif
    io = MMCIFIO()
    io.set_structure(structure)
    io.save(ciffile)


@app.command("multi_pdb_to_mmcif")
def multi_pdb_to_mmcif(pdb_files_dir: str, out_dir: str = None, verbose: bool = False):
    """
    Convert multiple PDB to mmcif format in one run.

    Parameters
    ----------
    pdb_files_dir : str
        Path to directory with multiple mmCIF input files.
    out_dir : str
        Output directory for PDB files.
    verbose : bool
        Verbose output.
    """
    out_dir = out_dir or Path.cwd()
    for file in Path(pdb_files_dir).iterdir():
        if file.suffix == ".pdb":
            pdb_to_mmcif(
                cif_file=str(file),
                pdb_file=f"{out_dir}/{file.stem}.pdb",
                verbose=verbose,
            )


def main():
    """
    Main entrypoint for the CLI.
    """
    app()


if __name__ == "__main__":
    """
    Main entrypoint for the script.
    """
    main()
