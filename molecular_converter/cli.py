"""
CLI to convert mmCIF files to PDB format.

Usage:
    $ molconverter cif_file [pdb_file] [--verbose]
"""

import sys
import logging
from pathlib import Path
from typing_extensions import Annotated

from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB import PDBIO, PDBParser
from Bio.PDB.mmcifio import MMCIFIO
import typer

from molecular_converter.exceptions import OutOfChainsError
from molecular_converter.utils import int_to_chain, rename_chains

app = typer.Typer()


@app.command("mmcif_to_pdb")
def mmcif_to_pdb(cif_file: Path, pdb_file: Path = None, verbose: bool = False):
    """
    Convert mmCIF to PDB format.

    Parameters
    ----------
    ciffile : Path
        Path to mmCIF input file.
    pdbfile : Path
        Path to PDB output file. Default is `{cif_file}.pdb`.
    verbose : bool
        Verbose output.
    """
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if verbose else logging.WARN,
    )

    ciffile = cif_file
    pdbfile = str(pdb_file) or f"{cif_file.stem}.pdb"
    # Not sure why biopython needs this to read a cif file
    strucid = ciffile.stem if len(str(ciffile)) > 4 else "1xxx"

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
def multi_mmcif_to_pdb(
    cif_files_dir: Path, out_dir: Path = None, verbose: bool = False
):
    """
    Convert multiple mmCIF to PDB format in one run.

    Parameters
    ----------
    dir_with_cif_files : Path
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
                cif_file=file,
                pdb_file=out_dir / f"{file.stem}.pdb",
                verbose=verbose,
            )


@app.command("multi_pdb_to_mmcif")
def multi_pdb_to_mmcif(
    pdb_files_dir: Path, out_dir: Path = None, verbose: bool = False
):
    """
    Convert multiple PDB files to mmCIF format in one run.

    Parameters
    ----------
    dir_with_cif_files : Path
        Path to directory with multiple PDB input files.
    out_dir : str
        Output directory for mmCIF files.
    verbose : bool
        Verbose output.
    """
    out_dir = out_dir or Path.cwd()
    for file in Path(pdb_files_dir).iterdir():
        if file.suffix == ".cif":
            pdb_to_mmcif(
                pdb_file=file,
                cif_file=out_dir / f"{file.stem}.cif",
                verbose=verbose,
            )


@app.command("pdb_to_mmcif")
def pdb_to_mmcif(pdb_file: Path, cif_file: Path = None, verbose: bool = False):
    """
    Convert PDB to mmCIF format.

    Parameters
    ----------
    pdbfile : Path
        Path to PDB input file.
    ciffile : Path
        Path to mmCIF output file. Default is `{pdb_file}.pdb`.
    verbose : bool
        Verbose output.
    """
    # TODO: DRY?
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if verbose else logging.WARN,
    )

    pdbfile = pdb_file
    cifffile = str(cif_file) or f"{pdb_file.stem}.pdb"
    # Not sure why biopython needs this to read a cif file
    strucid = pdbfile.stem if len(str(pdbfile)) > 4 else "1xxx"

    # Read file
    parser = PDBParser()
    structure = parser.get_structure(strucid, pdbfile)

    # Write mmCIF
    io = MMCIFIO()
    io.set_structure(structure)
    io.save(cifffile)


def __main__():
    """
    Main entrypoint for the CLI.
    """
    app()


if __name__ == "__main__":
    """
    Main entrypoint for the script.
    """
    app()
