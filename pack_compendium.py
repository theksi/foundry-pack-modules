import json
import os
import logging
import shutil
import urllib.parse
"""
This script analyze a foundryvtt module then pack all assets
"""

# Globals
# Use MODULE_ROOT and MODULE_NAME, COMPENDIUM_NAME if no args are set
MODUKE_NAME="pfs-s03"
MODULE_ROOT="modules"  # The Base directory for modules
MODULE_NAME="pfs-s03"
MODULE_PACK_DIR="packs"
MODULE_ASSETS_DIR="assets"
# FOUNDRYVTT information
FOUNDRYVTT_BASE_DIR="/Users/ksi/Documents/foundryvtt/Data/"
FOUNDRY_SRC_WORLD="pfs-prep"
COMPENDIUM_NAME="pfs-s03-scenes.db"
def load_compendium(location):
    entries = []
    with open(location) as openfileobject:
        for line in openfileobject:
            entries.append(json.loads(line))
    openfileobject.close()
    return(entries)
def generate_module_from_pack(compendium_items, type, foundry_base, module_base) :
    if type=='actors':
        new_compendium=pack_actors(compendium_items,foundry_base, module_base)
    elif type=='scenes':
        new_compendium=pack_scenes(compendium_items,foundry_base, module_base)
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
            print('OK Corral')
            new_item['img']=copy_asset(clean_string(item['img']),foundry_base, module_base)
        if 'tiles' in new_item :
            for tile in new_item['tiles']:
                if 'img' in tile:
                    print(f"tile image found in {new_item['name']} - tile {tile['_id']}: {tile['img']}")
                    tile['img']=copy_asset(clean_string(tile['img']),foundry_base, module_base)
        packed_compendium.append(new_item)
    return packed_compendium
def write_updated_compendium(compendium, location):
    f=open(location,"w")
    for item in compendium:
        f.write(json.dumps(item)+'\n')
    f.close()
    print(f"Updated compendium saved to {location}")

def clean_string(image_name):
    """
    removes characters following ? in the image URL 
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
    generate_module_from_pack(compendium_items,'scenes', FOUNDRYVTT_BASE_DIR, MODULE_ROOT+'/'+MODULE_NAME)
    # Ensure to create the module directory structure if doesn't exist !! 



if __name__ == "__main__":
    main()


