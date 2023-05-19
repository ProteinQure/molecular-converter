# Molecular File Converter

The Molecular File Converter is designed to seamlessly convert between the Protein Data Bank (PDB) and the Macromolecular Crystallographic Information File (mmCIF) format. These types of conversions are typically needed when downloading data from the RCSB databank - depending on the computational biology tool at hand you either need input files in PDB or mmCIF format. This converter makes it easy to switch back and forth between them.

Designed with a user-friendly interface, Molecular File Converter is crafted to be intuitively accessible to both novices and experienced users alike. It provides an easily navigable conversion process that significantly reduces the amount of time and effort researchers typically invest in manually transforming these file types. Additionally, the software is capable of batch conversions, enabling users to process multiple files concurrently.

## How to install

The install the package dependencies run

```
$ poetry install
```

Then activate the

```
$ poetry shell
```

and you should be ready to go!

## How to convert

You can find example input files in `data/mmcif_files` and `data/pdb_files`. Here's an example how to convert from mmCIF to PDB:

```
$ molconverter data/mmcif_files/7lcj.cif --pdb-file converted_7lcj.pdb
```

which will create a new file called `converted_7lcj.pdb` in the current working directory.

## How to test

You can execute the test suite locally by running

```
pytest .
```

The tests can be found in the `tests/` directory.
