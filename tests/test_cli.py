"""
Testing the `molconverter` CLI.
"""

from pathlib import Path
import plumbum
import tempfile

from molecular_converter.paths import PKG_DATA_DIR


def test_mmcif_to_pdb_cli():
    """
    Testing the conversion of mmCIF to PDB files.
    """
    molconverter = plumbum.local["molconverter"]
    with tempfile.TemporaryDirectory() as tmp_dir:
        outfile = f"{tmp_dir}/converted_7lcj.pdb"
        molconverter[
            "mmcif_to_pdb",
            f"{PKG_DATA_DIR}/mmcif_files/7lcj.cif",
            "--pdb-file",
            outfile,
        ]()
        assert Path(outfile).exists()
        assert Path(outfile).is_file()


def test_pdb_to_mmcif_cli():
    """
    Testing the conversion of PDB to MMCIF files.
    """
    molconverter = plumbum.local["molconverter"]
    with tempfile.TemporaryDirectory() as tmp_dir:
        outfile = f"{tmp_dir}/converted_7lcj.cif"
        molconverter[
            "pdb_to_mmcif", f"{PKG_DATA_DIR}/pdb_files/7lcj.pdb", "--cif-file", outfile
        ]()
        assert Path(outfile).exists()
        assert Path(outfile).is_file()


def test_multi_mmcif_to_pdb_cli():
    """
    Testing the conversion of multiple mmCIF to PDB files in one run.
    """
    molconverter = plumbum.local["molconverter"]
    with tempfile.TemporaryDirectory() as tmp_dir:
        molconverter[
            "multi_mmcif_to_pdb", f"{PKG_DATA_DIR}/mmcif_files", "--out-dir", tmp_dir
        ]()
        num_input_files = len(
            [
                file
                for file in (PKG_DATA_DIR / "mmcif_files").iterdir()
                if file.suffix == ".cif"
            ]
        )
        # ensure correct number of output files
        assert len(list(Path(tmp_dir).iterdir())) == num_input_files
        # make sure all output files have the .pdb suffix
        assert all(
            [
                file
                for file in Path(tmp_dir).iterdir()
                if file.suffix == ".pdb" and ".cif" not in file
            ]
        )
