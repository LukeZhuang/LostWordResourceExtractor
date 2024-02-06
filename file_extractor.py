#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
The tools to extract specific images and monobahaviours
"""

import json
import UnityPy
from util import process_asset_path


def extract_image(output_file_path, bundle_file_path, file_signature):
    found = False
    bundle = UnityPy.load(bundle_file_path)
    for path, obj in bundle.container.items():
        if obj.type.name in ["Texture2D", "Sprite"]:
            data = obj.read()
            extract_file_info = process_asset_path(path)
            if file_signature == extract_file_info:
                assert not found
                found = True
                print("saving", output_file_path)
                data.image.save(output_file_path)
    assert found


def extract_monobehaviour(output_file_path, bundle_file_path, file_signature):
    bundle = UnityPy.load(bundle_file_path)
    # First, try to find the entry object, whose "container" should match the file path
    entry_obj = None
    for obj in bundle.assets[0].objects.values():
        if obj.type.name != "MonoBehaviour":
            continue
        game_object = obj.read()
        # game_object.container is a path to the asset and it should be
        # only one of it which is the entrance
        if game_object.name and game_object.container:
            extract_file_info = process_asset_path(game_object.container)
            if file_signature == extract_file_info:
                assert not entry_obj
                print("saving", output_file_path)
                entry_obj = game_object
    assert entry_obj

    # After we found the entry obj, it should contains a list of pathIDs,
    # which indicating the order of its child scripts

    # (don't know why but its name may be "m_odrlist" or "m_ordrlist")
    if hasattr(entry_obj, "m_odrlist"):
        odrlist = entry_obj.m_odrlist
    elif hasattr(entry_obj, "m_ordrlist"):
        odrlist = entry_obj.m_ordrlist
    else:
        raise Exception("no orderlist")

    decoded_odr_list: list[dict[str, dict]] = []
    for odr in odrlist:
        assert hasattr(odr, "m_PathID")
        odr_obj = bundle.assets[0].objects[odr.path_id].read()
        # decoded_odr is a dict (can be parsed into json) of the child script
        decoded_odr = odr_obj.read_typetree()
        # create a wrapper with its name
        odr_wrapper_with_name: dict[str, dict] = {}
        assert hasattr(odr_obj, "m_Script")
        script = odr_obj.m_Script.read()
        script_name = script.m_Name
        assert script_name
        odr_wrapper_with_name[script_name] = decoded_odr
        decoded_odr_list.append(odr_wrapper_with_name)

    # Finally create a wrapper with some name to make it a json
    output_dict: dict[str, list[dict[str, dict]]] = {}
    output_dict["order_list"] = decoded_odr_list
    with open(output_file_path, "w", encoding="utf-8") as json_file:
        json.dump(output_dict, json_file, ensure_ascii=False, indent=4)
