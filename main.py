#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
"""

import json
import os
import sys
import wget
from util import process_asset_path, read_bundle_dict
from file_extractor import extract_image, extract_monobehaviour


download_url_prefix = (
    "http://thcdn.gggamedownload.com/source/Assetbundle_Android_v5016/"
)
# download_url_prefix = "http://d3s38hlip7moa.cloudfront.net/assetbundle/android/20240117_141128/0XDngEOS"
download_dir = sys.argv[1]
dicts_dir = sys.argv[2]
output_dir = sys.argv[3]

# only download and extract these types
# Need to coordinate with process_asset_path in util.py
supported_asset_types: set[int] = set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 100, 101])

manifest_file_path = os.path.join(".", "manifest.json")
print("downloading manifest")
try:
    manifest_url = download_url_prefix + "manifest.json"
    output = wget.download(manifest_url, manifest_file_path, bar=None)
except Exception:
    print("download manifest failed, exiting")
    sys.exit(1)

asset_list_path = os.path.join(dicts_dir, "asset_list.csv")
bundle_dict_path = os.path.join(dicts_dir, "bundle_dict.csv")
new_download_files_path = os.path.join(dicts_dir, "new_download_files.txt")
env_info_path = os.path.join(dicts_dir, "env_info.txt")


# manifest file to two dicts
manifest_file = open(manifest_file_path)
manifest = json.load(manifest_file)
asset_infos = manifest["AssetInfos"]
asset_list: list[tuple[int, str, str, str]] = []
bundle_dict: dict[str, str] = {}

for asset_info in asset_infos:
    bundle_file_name = asset_info["Name"]
    hash_code = asset_info["Hash"]
    asset_paths = asset_info["AssetPaths"]
    for asset_path in asset_paths:
        if output_file_info := process_asset_path(asset_path):
            file_type, out_dir, out_subdir, output_file_name = output_file_info
            if file_type not in supported_asset_types:
                continue
            asset_list.append(
                (file_type, out_dir, out_subdir, output_file_name, bundle_file_name)
            )
            bundle_dict[bundle_file_name] = hash_code

# read old bundle_dict if exists
old_bundle_dict: dict[str, str] | None = None
if os.path.exists(bundle_dict_path):
    old_bundle_dict = read_bundle_dict(bundle_dict_path)

# walk through download directory, delete files that are not in new bundle_list
# or the file has different hashcode in old and new (which means deprecated)
for df in os.listdir(download_dir):
    if df not in bundle_dict:
        os.remove(os.path.join(download_dir, df))
        print(df, "is removed due to not existing in new bundle_dict")
    elif (
        old_bundle_dict is not None
        and df in old_bundle_dict
        and old_bundle_dict[df] != bundle_dict[df]
    ):
        os.remove(os.path.join(download_dir, df))
        print(df, "is removed due to different hashcode in old/new bundle dict")

# collect all the files that are new in current manifest or have different hashcode
# we only need to download and extract these files
new_download_bundles: set[str] = set()
for bundle_file_name, bundle_file_hash in bundle_dict.items():
    if (
        old_bundle_dict is None
        or bundle_file_name not in old_bundle_dict
        or old_bundle_dict[bundle_file_name] != bundle_file_hash
    ):
        new_download_bundles.add(bundle_file_name)

# download new files
print("need to download", len(new_download_bundles), "files this time")
for bundle_file_name in sorted(new_download_bundles):
    bundle_file_path = os.path.join(download_dir, bundle_file_name)
    if not os.path.exists(bundle_file_path):
        print("downloading", bundle_file_name)
        try:
            bundle_download_url = download_url_prefix + bundle_file_name
            output = wget.download(bundle_download_url, bundle_file_path, bar=None)
        except Exception:
            print("downloading " + bundle_file_name + " failed, exiting")
            sys.exit(1)

# extract files by type
for file_type, out_dir, out_subdir, output_file_name, bundle_file_name in sorted(
    asset_list
):
    if file_type not in supported_asset_types:
        continue

    # we only need to care about the new bundle files
    if bundle_file_name not in new_download_bundles:
        continue

    # create a path to output_file
    assert output_dir != ""
    output_file_path = os.path.join(output_dir, out_dir)
    if not os.path.exists(output_file_path):
        os.mkdir(output_file_path)
    if out_subdir != "":
        output_file_path = os.path.join(output_file_path, out_subdir)
        if not os.path.exists(output_file_path):
            os.mkdir(output_file_path)

    output_file_path = os.path.join(output_file_path, output_file_name)
    bundle_file_path = os.path.join(download_dir, bundle_file_name)
    print("extracing file:", output_file_path, "from bundle:", bundle_file_path)

    # for finding corresponding file in bundle file
    file_signature = (file_type, out_dir, out_subdir, output_file_name)

    if file_type >= 0 and file_type < 100:
        # this is an image type
        extract_image(output_file_path, bundle_file_path, file_signature)
    elif file_type >= 100 and file_type < 200:
        # this is a scripted json type
        extract_monobehaviour(output_file_path, bundle_file_path, file_signature)
    else:
        raise Exception("unknown file type: " + str(file_type))

# after all extracting is done, write csvs
# It's only safe to do this after all download/extracting is done
# because it will overwrite those csvs
with open(asset_list_path, "w") as asset_list_file:
    asset_list_file.write("type,out_dir,out_subdir,file_name,bundle_file_name\n")
    for file_type, out_dir, out_subdir, output_file_name, bundle_file_name in sorted(
        asset_list
    ):
        fields = [
            str(file_type),
            out_dir,
            out_subdir,
            output_file_name,
            bundle_file_name,
        ]
        asset_list_file.write(",".join(fields) + "\n")

with open(bundle_dict_path, "w") as bundle_dict_file:
    bundle_dict_file.write("bundle_file_name,bundle_file_hash\n")
    for bundle_file_name, bundle_file_hash in sorted(bundle_dict.items()):
        bundle_dict_file.write(bundle_file_name + "," + bundle_file_hash + "\n")

with open(new_download_files_path, "w") as new_download_files:
    for bundle_file_name in sorted(new_download_bundles):
        new_download_files.write(bundle_file_name + "\n")

with open(env_info_path, "w") as env_info_file:
    env_info_file.write("download_url_prefix=" + str(download_url_prefix) + "\n")
    env_info_file.write(
        "supported_asset_types=" + str(sorted(supported_asset_types)) + "\n"
    )

os.remove(manifest_file_path)
