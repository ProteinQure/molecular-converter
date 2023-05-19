# Pair programming exercise

Welcome to the PQ pair programming exercise!

You & your partner have 90min to work on the exercises below. Make sure to first carefully read this file as well as the `README.md` before getting started. The exercise is designed in a way that should leave plenty of time to finish all the tasks. Don't be surprised if you finish early!

Please use whatever IDE or developer tools that you would usually use in your day-to-day. We also encourage you to use any online resources and please feel free to use ChatGPT.


## Exercise #1

Follow the installation instructions in the `README.md`. Then try a conversion from mmCIF to PDB file format by using one of the files in `data/mmcif_file`. Verify that everything is working as expected on the `master` branch.


## Exercise #2

Check out the `improved_cli` branch which adds the ability to convert multiple mmCIF files in one run. Rerun `poetry install` and make sure that the tests are passing and that the CLI is still working. If not, use your favourite debugger to resolve the bug.


## Exercise #3

In the README the tool claims that it can do mmCIF->PDB as well as PDB->mmCIF conversions. However, the tool is currently only able to convert from mmCIF->PDB. Stay on the `improved_cli` branch and implement the PDB->mmCIF conversion. At the end the CLI should have four subcommands for the two different conversions (+ 2 multi conversion options) which should work as follows:

```
$ molconverter mmcif_to_pdb data/mmcif_files/7lcj.cif --pdb-file converted_7lcj.pdb
$ molconverter multi_mmcif_to_pdb data/mmcif_files --out-dir data/out

$ molconverter pdb_to_mmcif data/pdb_files/7lcj.pdb --cif-file converted_7lcj.cif
$ molconverter multi_pdb_to_mmcif data/pdb_files --out-dir data/out
```


## Exercise #4

Some of your users complain that converting larger numbers of files takes too much time. You can test this by unzipping the `batch*.zip` files in `data/mmcif_files` and `data/pdb_files` and using them as inputs as follows:

```
$ molconverter multi_mmcif_to_pdb data/mmcif_files --out-dir data/out
$ molconverter multi_pdb_to_mmcif data/mmcif_files --out-dir data/out
```

Analyse the code base, find the bottleneck(s) and improve the CLI runtime!


## Exercise #5

If you happen to have extra time, let's make sure that this project is ready to be open-sourced: Clean up the code base as you see fit, ensure reliable & high quality code and maybe even implement a simple CI pipeline.
