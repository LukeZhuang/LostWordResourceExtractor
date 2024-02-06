# Touhou LostWord Resource Extractor
This is a tool which can manage different versions of touhou lostword resources and incrementally download/extract them.

It use several files to record history versions. When there comes a new resource version, it will automatically remove deprecated bundle files and only download and extract new ones.

The usage:

```cmd
mkdir download_dir
mkdir dicts_dir
mkdir output_dir
python3 main.py download_dir dicts_dir output_dir
```

It will create three files in `dicts_dir`:

1. `asset_list.csv`: the files that need to be extracted, which contains: file type (an integer), the uppermost output directory, inner output directory, output file name (so the output file path will be `output_dir/out_dir/out_subdir/output_file_name`), the bundle file name that containing it
2. `bundle_dict.csv`: all the bundle files in manifest that need to be download and processed, containing both the file name and hashcode
3. `new_download_files.txt`: the new bundle file names compared to the last resource version. We only need to download and extract from these files this time

Please **do not** delete all the files in the directories by hand because the script itself should manage them.
