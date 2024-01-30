#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
"""

import csv
import os
import sys
import wget
from manifest_processor import manifest_to_csvs

download_url_prefix = (
    "http://thcdn.gggamedownload.com/source/Assetbundle_Android_v4009/"
)
# download_url_prefix = "http://d3s38hlip7moa.cloudfront.net/assetbundle/android/20240117_141128/0XDngEOS"
download_dir = sys.argv[1]
dicts_dir = sys.argv[2]

manifest_file_path = os.path.join(".", "manifest.json")
try:
    manifest_url = download_url_prefix + "manifest.json"
    output = wget.download(manifest_url, manifest_file_path)
except Exception:
    print("download manifest failed, exiting")
    sys.exit(1)

asset_list_path = os.path.join(dicts_dir, "asset_list.csv")
bundle_dict_path = os.path.join(dicts_dir, "bundle_dict.csv")
manifest_to_csvs(manifest_file_path, download_dir, asset_list_path, bundle_dict_path)
os.remove(manifest_file_path)

with open(bundle_dict_path) as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        bundle_file_name = row["bundle_file_name"]
        bundle_file_path = os.path.join(download_dir, bundle_file_name)
        if not os.path.exists(bundle_file_path):
            try:
                bundle_download_url = download_url_prefix + bundle_file_name
                output = wget.download(bundle_download_url, bundle_file_path)
            except Exception:
                print("downloading " + bundle_file_name + "failed, exiting")
                sys.exit(1)
