from distutils.command.clean import clean
import json
import os
import logging
import shutil
import urllib.parse
from bs4 import BeautifulSoup as bs
import re
from compendiumlib import compendiumlib as cl
"""
This script analyze a foundryvtt module then pack all assets
"""
# Globals
# Use MODULE_ROOT and MODULE_NAME, COMPENDIUM_NAME if no args are set
MODULE_ROOT="./modules"  # The Base directory for modules
MODULE_NAME="test"
MODULE_PACK_DIR="packs"
MODULE_ASSETS_DIR="assets"
# FOUNDRYVTT information
FOUNDRYVTT_BASE_DIR="/Users/ksi/Documents/foundryvtt/Data/"
FOUNDRY_SRC_WORLD="pfs-prep"
COMPENDIUM_NAME="pfs-s01.db"


def main():
    # Generate target directory tree
    target_dir=f"{MODULE_ROOT}/{MODULE_NAME}"
    assets_base=f"{target_dir}/{MODULE_ASSETS_DIR}"
    target_pack_name=f"{target_dir}/{MODULE_PACK_DIR}/{MODULE_NAME}.db"
    # Loads adventure compendium
    cl.create_target_dir(target_dir,MODULE_PACK_DIR, MODULE_ASSETS_DIR)
    src_compendium=FOUNDRYVTT_BASE_DIR+"worlds/"+FOUNDRY_SRC_WORLD+"/packs/"+COMPENDIUM_NAME
    packed_adventures=[]
    adventures=cl.load_compendium(src_compendium)
    packed_adventures=cl.generate_adventure_compendium(adventures, FOUNDRYVTT_BASE_DIR, assets_base)
    cl.write_compendium(packed_adventures, target_pack_name)


if __name__ == "__main__":
    main()

