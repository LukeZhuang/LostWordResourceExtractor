#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
"""

import csv
import os
import sys
import UnityPy
from util import process_asset_path

bundles_dir = sys.argv[1]
asset_list_file = sys.argv[2]
output_dir = sys.argv[3]

with open(asset_list_file) as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        file_type = row["type"]
        out_dir = row["out_dir"]
        out_subdir = row["out_subdir"]
        file_name = row["file_name"]
        bundle_file_name = row["bundle_file_name"]
        if file_type != "0":
            continue

        assert out_dir != ""
        output_file_path = os.path.join(output_dir, out_dir)
        if not os.path.exists(output_file_path):
            os.mkdir(output_file_path)

        if out_subdir != "":
            output_file_path = os.path.join(output_file_path, out_subdir)
            if not os.path.exists(output_file_path):
                os.mkdir(output_file_path)

        output_file_path = os.path.join(output_file_path, file_name)
        bundle_file_path = os.path.join(bundles_dir, bundle_file_name)

        bundle = UnityPy.load(bundle_file_path)
        found = False
        for path, obj in bundle.container.items():
            if obj.type.name in ["Texture2D", "Sprite"]:
                data = obj.read()
                extract_file_info = process_asset_path(path)
                if (
                    int(file_type),
                    out_dir,
                    out_subdir,
                    file_name,
                ) == extract_file_info:
                    found = True
                    if not os.path.exists(output_file_path):
                        print("saving", output_file_path)
                        data.image.save(output_file_path)
        assert found
