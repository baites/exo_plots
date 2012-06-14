## diff.py

Compare keys in two ROOT files and report if these are different. The function
works in similar way to Linux _diff_ tool for text files.

The function scans only top level content and does not go into folders inside
ROOT file

The function returns a list with four items

0. True if files are different and False otherwise
1. keys that are found in the first file only
2. common to both files keys
3. keys that are found in the second file only

## Run

The module can also be run as a stand-alone script, e.g.:

```bash
python root/diff.py file1.root file2.root
# the script will return 0 if files are the same and 1 otherwise
echo $?
```

## Example

```python
# default use
different, lkeys, ckeys, rkeys = diff("file1.root", "file2.root")
if different:
    print("files are different")
    print("left only keys:", lkeys)
    print("right only keys:", rkeys)
    print("common keys:", ckeys)
```

the function may also be run in verbose mode and print unique keys found in the
first or second file if any:

```python
# verbose mode
diff("file1.root", "file2.root", verbose=True)
```
