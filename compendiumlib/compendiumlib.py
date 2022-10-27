import json
import os
import string
import shutil
import re
import urllib.parse
from bs4 import BeautifulSoup as bs


LOOKUP_KEYS=['img', 'content', 'src'] # List of key to lookup in the compendium - Other keys won't be processed
SINGLE_FILE_KEYS=['img', 'src', 'thumb'] # List keys containing images as a single string unlike content which is HTML
# Thoses assets are located under data/systems/.... and should not be moved. the path is not explicit each time
EXCLUDE_FILE_PATTERNS=['^icons\/*','^system\/*']
MAX_DEPTH=15 # the maximum recursion depth of brower_adventure_compendium()

# Helper functions
def item_is_included(item, regexes):
    excluded_pattern= "(" + ")|(".join(regexes) + ")"
    if re.match(excluded_pattern, item):
        return False
    else:
        return True
def create_target_dir(base_dir,pack_dir, asset_dir):
    print(f"Creating module base directories under {base_dir}")
    os.makedirs(base_dir,exist_ok=True)
    os.makedirs(f"{base_dir}/{pack_dir}",exist_ok=True)
    os.makedirs(f"{base_dir}/{asset_dir}",exist_ok=True)
def copy_asset(asset,foundry_base, asset_base):
    if asset:
        #print(f"file to move : {asset}, source_directory: {foundry_base}, Destination directory: {asset_base}")
        src=foundry_base+asset
        dst=f"{asset_base}/{os.path.basename(asset)}"
        # print(f"moving from \n {src} to \n {dst}\n")
        shutil.copyfile(urllib.parse.unquote(src), urllib.parse.unquote(dst))
        return(dst)
    else:
        print(f"empty string - doing nothing")
def clean_string(image_name):
    """
    Clean string containing the file name
    - removes characters following ? in the image URL 
    """
    file_name=image_name
    if image_name.find('?') >=0 :
        file_name=image_name[0:image_name.find('?')]
    return file_name      
def get_images_from_content(content):
        soup=bs(content, "lxml")
        return(soup.find_all('img'))
# compendium manipulations
def load_compendium(location):
    """
    Opens the compendium then loads it as a list of Dict
    """
    entries = []
    with open(location, encoding="utf-8") as openfileobject:
        for line in openfileobject:
            entries.append(json.loads(line))
    openfileobject.close()
    return(entries)
def write_compendium(compendium, location):
    f=open(location,"w", encoding="utf-8")
    for item in compendium:
        f.write(json.dumps(item,ensure_ascii=False)+'\n')
    f.close()
    print(f"Updated compendium saved to {location}")
def pack_component(adventure, key, foundry_base, asset_base):
    if key in SINGLE_FILE_KEYS:
        print(f"processing {key} : {adventure}")
        if item_is_included(adventure, EXCLUDE_FILE_PATTERNS):
            return(copy_asset(clean_string(adventure),foundry_base, asset_base))
    if key== 'content':
        #print(f"processing {key} : {adventure}")
        images=get_images_from_content(adventure)
        print(images)
        for image in images:
            new_image=copy_asset(clean_string(image['src']),foundry_base, asset_base)
            adventure=re.sub(image['src'], new_image, adventure)
    return(adventure)
def browse_adventure_compendium(adventure, depth, foundry_base, asset_base):
    # print(f"browse_adventure_compendium current depth= {depth}")
    depth+= 1
    if depth >= MAX_DEPTH:
        return adventure
    if not isinstance(adventure, dict) or isinstance(adventure, list):
        return adventure
    for key in adventure:
        if isinstance(adventure[key], str) and key in LOOKUP_KEYS:
            adventure[key]=pack_component(adventure[key],key, foundry_base, asset_base)
            # print(f"{key} will be processed and assets {adventure[key]} packed into the module")

        if isinstance(adventure[key], dict):
            # print(f"browsing {adventure[key]}")
            adventure[key]=browse_adventure_compendium(adventure[key], depth, foundry_base, asset_base)
        if isinstance(adventure[key], list):
            for item in  adventure[key]:
                # print(f"browsing {item}")
                # print(type(item))
                item=browse_adventure_compendium(item, depth, foundry_base, asset_base)
    return adventure
def generate_adventure_compendium(adventures, foundry_base, asset_base):
    for adventure in adventures:
        depth=0
        adv_name=adventure['name'].replace(" ", "")
        print(f"Processing adventure named {adv_name}")
        print(f"Creating Adventure asset directory: {asset_base}/{adv_name}")
        adv_asset_dir=f"{asset_base}/{adv_name}"
        os.makedirs(adv_asset_dir, exist_ok=True)
        print(adv_asset_dir)
        adventure=browse_adventure_compendium(adventure,depth, foundry_base, adv_asset_dir)
    return(adventures)

### helper functions
 