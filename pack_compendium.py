from distutils.command.clean import clean
import json
import os
import logging
import shutil
import urllib.parse
from bs4 import BeautifulSoup as bs
import re
"""
This script analyze a foundryvtt module then pack all assets
"""

# Globals
# Use MODULE_ROOT and MODULE_NAME, COMPENDIUM_NAME if no args are set
MODULE_ROOT="./modules"  # The Base directory for modules
MODULE_NAME="pfs-s01"
MODULE_PACK_DIR="packs"
MODULE_ASSETS_DIR="assets"
# FOUNDRYVTT information
FOUNDRYVTT_BASE_DIR="/Users/ksi/Documents/foundryvtt/Data/"
FOUNDRY_SRC_WORLD="pfs-prep"
COMPENDIUM_NAME="pfs-saison1-journal.db"
COMPENDIUM_TYPE="journal"
def load_compendium(location):
    entries = []
    with open(location, encoding="utf-8") as openfileobject:
        for line in openfileobject:
            entries.append(json.loads(line))
    openfileobject.close()
    return(entries)
def generate_module_from_pack(compendium_items, type, foundry_base, module_base) :
    if type=='actors':
        new_compendium=pack_actors(compendium_items,foundry_base, module_base)
    elif type=='scenes':
        new_compendium=pack_scenes(compendium_items,foundry_base, module_base)
    elif type=='journal':
        new_compendium=pack_journal(compendium_items,foundry_base, module_base)

    else:
        raise NameError('Unsupported compendium type: '+type)
    write_updated_compendium(new_compendium,module_base+'/'+MODULE_PACK_DIR+'/'+COMPENDIUM_NAME)
    
def pack_actors(compendium_items,foundry_base, module_base):
    """
    read through the compendium_items  
    - copy images to the module directory
    - returns a new compendium items with update path
    """
    packed_compendium=[]
    for item in compendium_items:
        new_item=item
        print(f"Processing entry named {item['name']}")
        new_item['img']=copy_asset(clean_string(item['img']),foundry_base, module_base)
        new_item['token']['img']=copy_asset(clean_string(item['token']['img']),foundry_base, module_base)
        packed_compendium.append(new_item)
    return packed_compendium
def pack_journal(compendium_items,foundry_base, module_base):
    """
    read through the compendium_items  
    - copy images to the module directory
    - returns a new compendium items with update path
    """
    packed_compendium=[]
    for item in compendium_items:
        new_item=item
        print(f"Processing entry named {item['name']}")
        if 'img' in new_item.keys():
            if new_item['img'] is not None:
                new_item['img']=copy_asset(clean_string(item['img']),foundry_base, module_base)
        packed_compendium.append(new_item)
        if 'content' in new_item.keys():
            images=get_images_from_content(new_item['content'])
            for image in images:
                new_image=copy_asset(clean_string(image['src']),foundry_base, module_base)
                new_item['content']=re.sub(image['src'], new_image, new_item['content'])
    return packed_compendium

def get_images_from_content(content):
        soup=bs(content, "lxml")
        return(soup.find_all('img'))

def pack_scenes(compendium_items,foundry_base, module_base):
    """
    read through the compendium_items  
    - copy images to the module directory
    - returns a new compendium items with update path
    """
    packed_compendium=[]
    for item in compendium_items:
        new_item=item
        print(f"Processing entry named {item['name']}")
        if 'img' in new_item:
            new_item['img']=copy_asset(clean_string(item['img']),foundry_base, module_base)
        if 'tiles' in new_item :
            for tile in new_item['tiles']:
                if 'img' in tile:
                    print(f"tile image found in {new_item['name']} - tile {tile['_id']}: {tile['img']}")
                    tile['img']=copy_asset(clean_string(tile['img']),foundry_base, module_base)
        packed_compendium.append(new_item)
    return packed_compendium
def write_updated_compendium(compendium, location):
    f=open(location,"w", encoding="utf-8")
    for item in compendium:
        f.write(json.dumps(item,ensure_ascii=False)+'\n')
    f.close()
    print(f"Updated compendium saved to {location}")

def clean_string(image_name):
    """
    removes characters following ? in the image URL 
    soup=bs(content_value) et ensuite images=soup.find('img') --> on récupère une liste des images qui ressemble à ça:
    <img height="1290" src="pfs-3-01/Market%20square.png" width="1038"/>
    Ensuite on peut récupèrer le src avec images('src')

    """
    file_name=image_name
    if image_name.find('?') >=0 :
        file_name=image_name[0:image_name.find('?')]
    return file_name

def copy_asset(asset,foundry_base, module_base):
    print(f"file to move : {asset}, source_directory: {foundry_base}, Destination directory: {module_base}")
    src=foundry_base+asset
    dst=module_base+"/"+MODULE_ASSETS_DIR+'/'+os.path.basename(asset)
    #print(f"copying {src} to {dst}")
    shutil.copyfile(urllib.parse.unquote(src), urllib.parse.unquote(dst))
    return(dst)


def main():
    src_compendium=FOUNDRYVTT_BASE_DIR+"worlds/"+FOUNDRY_SRC_WORLD+"/packs/"+COMPENDIUM_NAME
    updated_compendium=[]
    compendium_items=load_compendium(src_compendium)
    ## on sait que l'erreur viens après
     #   soit via bs4, soit via urllib ? 
    updated_compendium=generate_module_from_pack(compendium_items,COMPENDIUM_TYPE, FOUNDRYVTT_BASE_DIR, MODULE_ROOT+'/'+MODULE_NAME)
    # Ensure to create the module directory structure if doesn't exist !! 



if __name__ == "__main__":
    main()


