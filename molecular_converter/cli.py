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
from Bio.PDB.mmcifio import MMCIFIO
from Bio.PDB import PDBIO
import typer
import os
import tempfile
from dask import delayed, compute

from molecular_converter.exceptions import OutOfChainsError
from molecular_converter.utils import int_to_chain, rename_chains

app = typer.Typer()


def convert_to_pdb(cif_file, out_dir, molconverter):
    with tempfile.TemporaryDirectory() as tmp_dir:
        outfile = f"{tmp_dir}/{out_dir}"
        molconverter[
            "mmcif_to_pdb",
            cif_file,
            "--pdb-file",
            outfile,
        ]()
        assert Path(outfile).exists()
        assert Path(outfile).is_file()
        return outfile


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

    pdbfile = pdb_file or cif_file.split(".")[0] + ".pdb"
    # Not sure why biopython needs this to read a cif file
    strucid = cif_file[:4] if len(cif_file) > 4 else "1xxx"

    # Read file
    parser = MMCIFParser()
    structure = parser.get_structure(strucid, cif_file)

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

    io.save(str(pdbfile))


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
    cif_files = list(Path(cif_files_dir).iterdir())
    out_dir = Path(out_dir) or Path.cwd()
    compute(
        *[
            delayed(mmcif_to_pdb)(
                str(cif_file), str(out_dir / (cif_file.stem + ".pdb"))
            )
            for cif_file in cif_files
        ]
    )


@app.command("pdb_to_mmcif")
def pdb_to_mmcif(pdb_file: str, cif_file: str = None, verbose: bool = False):
    """
    Convert PDB to mmCIF format.

    Parameters
    ----------
    pdbfile : str
        Path to PDB input file.
    mmciffile : str
        Path to mmCIF output file. Default is `{pdb_file}.cif`.
    verbose : bool
        Verbose output.
    """
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if verbose else logging.WARN,
    )

    file_name = cif_file or pdb_file.split(".")[0] + ".cif"
    struct_id = pdb_file[:4] if len(pdb_file) > 4 else "1xxx"
    # Read file
    parser = PDBParser()
    structure = parser.get_structure(struct_id, pdb_file)

    # Write mmCIF
    io = MMCIFIO()
    io.set_structure(structure)

    io.save(str(file_name))


@app.command("multi_pdb_to_mmcif")
def multi_pdb_to_mmcif(pdb_files_dir: str, out_dir: str = None, verbose: bool = False):
    """
    Convert multiple PDB to mmCIF format in one run.

    Parameters
    ----------
    pdb_files_dir : str
        Path to directory with multiple PDB input files.
    out_dir : str
        Output directory for mmCIF files.
    verbose : bool
        Verbose output.
    """
    out_dir = Path(out_dir) if out_dir else Path.cwd()
    out_dir.mkdir(exist_ok=True)

    tasks = []
    for file in Path(pdb_files_dir).iterdir():
        if file.suffix == ".pdb":
            cif_file = out_dir / (file.stem + ".cif")
            task = delayed(pdb_to_mmcif)(str(file), str(cif_file))
            tasks.append(task)
    # Execute tasks in parallel
    compute(*tasks)


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
