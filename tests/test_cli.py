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
        molconverter[f"{PKG_DATA_DIR}/mmcif_files/7lcj.cif", "--pdb-file", outfile]()
        assert Path(outfile).exists()
        assert Path(outfile).is_file()
