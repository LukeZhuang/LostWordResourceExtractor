#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
This file processes manifest.json and rearrange it into two csv files, one
is sorted unified asset file name to bundle file name, the other one is sorted
bundle file name to hashcode. We incrementally maintain our bundle library by
removing deprecated bundles and downloading ones using these two files.
"""

import json
import os
from util import process_asset_path, read_bundle_dict


def manifest_to_csvs(
    manifest_file_path: str,
    download_dir: str,
    asset_list_path: str,
    bundle_dict_path: str,
) -> None:
    # manifest file to two dicts
    manifest_file = open(manifest_file_path)
    data = json.load(manifest_file)
    asset_infos = data["AssetInfos"]
    asset_list: list[tuple[str, str, str, str]] = []
    bundle_dict: dict[str, str] = {}
    for asset_info in asset_infos:
        bundle_file_name = asset_info["Name"]
        hash_code = asset_info["Hash"]
        asset_paths = asset_info["AssetPaths"]
        for asset_path in asset_paths:
            if output_file_info := process_asset_path(asset_path):
                file_type, out_dir, out_subdir, output_file_name = output_file_info
                asset_list.append(
                    (
                        str(file_type),
                        out_dir,
                        out_subdir,
                        output_file_name,
                        bundle_file_name,
                    )
                )
                bundle_dict[bundle_file_name] = hash_code

    # read old bundle_dict if exists
    old_bundle_dict: dict[str, str] | None = None
    if os.path.exists(bundle_dict_path):
        old_bundle_dict = read_bundle_dict(bundle_dict_path)

    # walk through download directory, remove files that are not in new bundle_list
    # or file has different hashcode in old_bundle_dict and bundle_dict
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
            print(df, "is removed due to different hashcode in old/new bundle_dict")

    # write asset_dict csv
    with open(asset_list_path, "w") as asset_list_file:
        asset_list_file.write("type,out_dir,out_subdir,file_name,bundle_file_name\n")
        for fields in sorted(asset_list):
            asset_list_file.write(",".join(fields) + "\n")

    # write bundle_dict csv
    with open(bundle_dict_path, "w") as bundle_dict_file:
        bundle_dict_file.write("bundle_file_name,bundle_file_hash\n")
        for bundle_file_name, bundle_file_hash in sorted(bundle_dict.items()):
            bundle_dict_file.write(bundle_file_name + "," + bundle_file_hash + "\n")


if __name__ == "__main__":
    pass
