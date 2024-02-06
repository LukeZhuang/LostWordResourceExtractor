#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
This file includes general helper functions
"""

import csv
import json
import os
import re


def match_pattern(asset_path: str, pattern: str) -> tuple[str] | None:
    g = re.findall(pattern, asset_path.lower())
    if len(g) > 0:
        assert len(g) == 1
        return g[0] if type(g[0]) is tuple else (g)
    return None


def is_alt_costume(costume_id: str) -> str:
    return "AltCostume" if costume_id != "01" else "Original"


# A function to unify a Unity bundle path to path info of output file,
# which is a tuple of output directory, subdirectory and file name
# Currently we only handle the following kinds of files
# The first element in the result is file type, in which:
# 0-99: image types, 100-199: monobehaviour (scripted json) types
def process_asset_path(asset_path: str) -> tuple[int, str, str, str] | None:
    # 1. unit square image:
    #      Assets/East/Units/1003/03/Thumbnail/Square.png
    #        -> UnitSquare/AltCostume/S100303.png
    if grp := match_pattern(
        asset_path, r"^assets/east/units/([0-9]+)/([0-9]+)/thumbnail/square.png$"
    ):
        return 0, "UnitSquare", is_alt_costume(grp[1]), "S" + grp[0] + grp[1] + ".png"

    # 2. unit gallery/pray image:
    #      Assets/East/Units/1003/06/Thumbnail/Costume.png
    #        -> UnitCostume/AltCostume/C100306.png
    elif grp := match_pattern(
        asset_path, r"^assets/east/units/([0-9]+)/([0-9]+)/thumbnail/costume.png$"
    ):
        return 1, "UnitCostume", is_alt_costume(grp[1]), "C" + grp[0] + grp[1] + ".png"

    # 3. unit half body image:
    #      Assets/East/Units/1003/03/Thumbnail/Change.png
    #        -> UnitChange/AltCostume/CH100303.png
    elif grp := match_pattern(
        asset_path, r"^assets/east/units/([0-9]+)/([0-9]+)/thumbnail/change.png$"
    ):
        return 2, "UnitChange", is_alt_costume(grp[1]), "CH" + grp[0] + grp[1] + ".png"

    # 4. unit full sprites:
    #      Assets/East/Units/1003/03/G100303/G100303.png
    #        -> UnitFullBody/AltCostume/G100303.png
    elif grp := match_pattern(
        asset_path, r"^assets/east/units/([0-9]+)/([0-9]+)/g([0-9]+)/g([0-9]+).png$"
    ):
        assert grp[0] == grp[2][:-2] and grp[0] == grp[3][:-2]
        assert grp[1] == grp[2][-2:]
        return 3, "UnitFullBody", is_alt_costume(grp[1]), "G" + grp[0] + grp[1] + ".png"

    # 5. unit icon face:
    #      Assets/East/Units/1100/01/Thumbnail/IconFace.png
    #        -> UnitIconFace/Original/IF110001.png
    elif grp := match_pattern(
        asset_path, r"^assets/east/units/([0-9]+)/([0-9]+)/thumbnail/iconface.png$"
    ):
        return (
            4,
            "UnitIconFace",
            is_alt_costume(grp[1]),
            "IF" + grp[0] + grp[1] + ".png",
        )

    # 6. unit shot/spellcard icon:
    #      Assets/East/Units/1003/04/UI/Sprite/spell_btn_a.png
    #        -> UnitShotIcon/AltCostume/SHB100304A.png
    elif grp := match_pattern(
        asset_path,
        r"^assets/east/units/([0-9]+)/([0-9]+)/ui/sprite/(shot|spell)_btn_([a-c]).png$",
    ):
        return (
            5,
            "UnitShotIcon",
            is_alt_costume(grp[1]),
            (
                ("SHB" if grp[2] == "shot" else "SPB")
                + grp[0]
                + grp[1]
                + grp[3].upper()
                + ".png"
            ),
        )

    # 7. picture square image:
    #      Assets/East/Pictures/319/ThumbSquare.png
    #        -> PictureSquare/PTS319.png
    elif grp := match_pattern(
        asset_path, r"^assets/east/pictures/([0-9]+)/thumbsquare.png$"
    ):
        return 6, "PictureSquare", "", "PTS" + grp[0] + ".png"

    # 8. picture gallery/pray image:
    #      Assets/East/Pictures/319/ThumbLarge.png
    #        -> PictureLarge/PTS319.png
    elif grp := match_pattern(
        asset_path, r"^assets/east/pictures/([0-9]+)/thumblarge.png$"
    ):
        return 7, "PictureLarge", "", "PTL" + grp[0] + ".png"

    # 9. picture full image:
    #      Assets/East/Pictures/319/Efuda.png
    #        -> PictureEfuda/PE319.png
    elif grp := match_pattern(asset_path, r"^assets/east/pictures/([0-9]+)/efuda.png$"):
        return 8, "PictureEfuda", "", "PE" + grp[0] + ".png"

    # 10. comic background:
    #       Assets/East/Graphics/Comic/BG/10340101.png
    #         -> ComicBackGround/CBG10340101.png
    elif grp := match_pattern(
        asset_path, r"^assets/east/graphics/comic/bg/([0-9]+).png$"
    ):
        return 9, "ComicBackGround", "", "CBG" + grp[0] + ".png"

    # 11. unit barrage timeline file:
    #      Assets/East/Units/1025/Timeline/Barrage10.asset
    #        -> Timeline/TB102510.asset
    elif grp := match_pattern(
        asset_path,
        r"^assets/east/units/([0-9]+)/timeline/barrage([12347])([0123]).asset$",
    ):
        return 100, "Timeline", "", "TB" + grp[0] + grp[1] + grp[2] + ".json"

    # 12. plot script file:
    #      Assets/East/Comics/uo/Event16/Extra/Episode4.asset
    #        -> Episode/EP_event16-extra-episode4.asset
    elif grp := match_pattern(asset_path, r"^assets/east/comics/uo/(.*)\.asset$"):
        return 101, "Comic", "", "-".join(grp[0].split("/")) + ".json"
    return None


def reformat_json(json_file_path: str) -> None:
    with open(json_file_path) as json_file:
        data = json.load(json_file)
        pretty_json = json.dumps(data, indent=4)
        output_path, _ = os.path.splitext(json_file_path)
        with open(output_path + "-reformatted.json", "w") as fo:
            fo.write(pretty_json)


def read_bundle_dict(bundle_dict_path: str) -> dict[str, str]:
    bundle_dict: dict[str, str] = {}
    with open(bundle_dict_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            bundle_dict[row["bundle_file_name"]] = row["bundle_file_hash"]
    return bundle_dict


# testing code
if __name__ == "__main__":
    print(process_asset_path("Assets/East/Units/1003/03/Thumbnail/Square.png"))
    print(process_asset_path("Assets/East/Units/1003/06/Thumbnail/Costume.png"))
    print(process_asset_path("Assets/East/Units/1003/03/Thumbnail/Change.png"))
    print(process_asset_path("Assets/East/Units/1003/03/G100303/G100303.png"))
    print(process_asset_path("Assets/East/Units/1100/01/Thumbnail/IconFace.png"))
    print(process_asset_path("Assets/East/Units/1003/04/UI/Sprite/spell_btn_a.png"))
    print(process_asset_path("Assets/East/Pictures/319/ThumbSquare.png"))
    print(process_asset_path("Assets/East/Pictures/319/ThumbLarge.png"))
    print(process_asset_path("Assets/East/Pictures/319/Efuda.png"))
    print(process_asset_path("Assets/East/Units/1025/Timeline/Barrage10.asset"))
    print(process_asset_path("Assets/East/Comics/uo/Event16/Extra/Episode4.asset"))
    reformat_json(
        os.path.join(os.path.join(".", "manifests"), "manifest_ch_v4009.json")
    )
