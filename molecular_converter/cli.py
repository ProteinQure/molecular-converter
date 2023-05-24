"""
CLI to convert between mmCIF and PDB formats. Includes methods of parallel
batch processing.

Usage:
    $ molconverter cif_file [pdb_file] [--verbose]
"""

import sys
import logging
from pathlib import Path

from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB import PDBIO, PDBParser
from joblib import Parallel, delayed
import typer

from molecular_converter.exceptions import OutOfChainsError
from molecular_converter.utils import rename_chains

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


@app.command("pdb_to_mmcif")
def pdb_to_mmcif(pdb_file: str, cif_file: str = None, verbose: bool = False):
    """
    Convert PDB to mmCIF format.

    Parameters
    ----------
    pdbfile : str
        Path to PDB output file. Default is `{cif_file}.pdb`.
    ciffile : str
        Path to mmCIF input file.
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
    parser = PDBParser()
    structure = parser.get_structure(strucid, pdbfile)

    # Write PDB
    io = PDBIO()
    io.set_structure(structure)
    io.save(ciffile)


@app.command("multi_mmcif_to_pdb")
def multi_mmcif_to_pdb(
    cif_files_dir: str,
    out_dir: str = None,
    verbose: bool = False
):
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
    Parallel(n_jobs=-1)(
        delayed(mmcif_to_pdb)(
            cif_file=str(file),
            pdb_file=f"{out_dir}/{file.stem}.cif",
            verbose=verbose
        )
        for file in Path(cif_files_dir).iterdir()
        if file.suffix == ".cif"
    )


@app.command("multi_pdb_to_mmcif")
def multi_pdb_to_mmcif(
    pdb_files_dir: str,
    out_dir: str = None,
    verbose: bool = False
):
    """
    Convert multiple PDB files to mmCIF format in one run.

    Parameters
    ----------
    pdb_files_dir : str
        Path to directory with multiple PDB input files.
    out_dir : str
        Output directory for mmCIF files.
    verbose : bool
        Verbose output.
    """
    out_dir = out_dir or Path.cwd()
    Parallel(n_jobs=-1)(
        delayed(pdb_to_mmcif)(
            pdb_file=str(file), cif_file=f"{out_dir}/{file.stem}.pdb", verbose=verbose
        )
        for file in Path(pdb_files_dir).iterdir()
        if file.suffix == ".pdb"
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
    app()
