import bpy
from collections import defaultdict
from bpy.types import Operator

### FIND SUBCLASSES OF CLASSES ###
# For modifiers, nodes, etc.
# Ignore the path cacher if the fixed type of a collection has many subclasses
# for example, bpy.types.Modifier doesn't explicitly have an ID property, but bpy.types.ArmatureModifier does

subs = defaultdict(set)

ignores = {
    bpy.types.Operator,
    bpy.types.Panel,
    bpy.types.PropertyGroup,
    bpy.types.Menu,
    bpy.types.UIList
}

for attr in dir(bpy.types):
    attr = getattr(bpy.types, attr)
    
    supers = getattr(attr, '__mro__', None)
    if not supers: continue

    supers = list(supers)
    if bpy.types.ID in supers:
        continue
    
    prior = supers.pop(0)
    try:
        while supers[0] != bpy.types.bpy_struct:
            prior = supers.pop(0)
    except IndexError:
        continue

    if prior in ignores:
        continue
    if prior == attr:
        continue
    
    subs[prior].add(attr)

#################

### PATH CACHER ###
# Pre-emptively go through all possible paths in any ID to see where an ID reference might be.
# Save these paths and restrict the search to the cache.

ID_types = [type.fixed_type for type in bpy.data.bl_rna.properties if isinstance(getattr(type, 'fixed_type', None), bpy.types.ID)]

valid_paths = defaultdict(set)
valid_paths[bpy.types.NodeTree.bl_rna].add('nodes')
valid_paths[bpy.types.Object.bl_rna].add('modifiers')
valid_paths[bpy.types.NodeTree.bl_rna].add('animation_data')
is_complete = defaultdict(bool)
visited = defaultdict(set)

def path_cacher(id, line, line_data):
    if id in line_data:
        return
    line_data = list(line_data)
    line_data.append(id)
    
    if is_complete[id]:
        if valid_paths[id]:
            [valid_paths[data].add(prop) for data, prop in line]
        return
    
    for attr_name, attr in sorted(id.bl_rna.properties.items(), key=lambda a: a[0]):
        if attr_name in {'rna_type', 'original', 'srna'}:
            continue
        if attr_name in visited[id]: continue
        fixed_type = getattr(attr, 'fixed_type', None)
        
        if not fixed_type: continue
        if attr_name in valid_paths[id]: continue
        if (isinstance(fixed_type, bpy.types.ID)) and (not isinstance(fixed_type, bpy.types.NodeTree)):
            [valid_paths[data].add(prop) for data, prop in line + [(id, attr_name)]]
            continue
        
        path_cacher(fixed_type, (line + [(id, attr_name)]), line_data)
        visited[id].add(attr_name)
    is_complete[id] = True

for id in ID_types:
    path_cacher(id, [], [])
################


### PATH FINDER ###
# The main logic behind path finding.

#obj = bpy.context.object

main_id = None

ignores = {
    bpy.types.Mesh: {'vertices'},
    bpy.types.PoseBone: {'parent', 'child'},
    bpy.types.EditBone: {'parent', 'child'},
    bpy.types.Bone: {'parent', 'child'},
    bpy.types.NodeTree: {'links'},
    bpy.types.Scene: {'view_layers'},
    bpy.types.Collection: {'children'},
}

def found(at):
    #if bpy.app.version >= (5, 0, 0):
    #    final = ''
    #    for attr in at[1:]:
    #        if attr.startswith('['):
    #            final += attr
    #        else:
    #            final += '.' + attr
    #    final = final.lstrip('.')
    #    path = main_id.path_resolve(final, False)
    #    print(path, repr(path), final)
    #    print(path.path_from_module())
    #
    #else:
    final = at[0]
    for attr in at[1:]:
        if attr.startswith('['):
            final += attr
        else:
            final += '.' + attr
    print(final)

def starter(id, line, line_data, target_id, ignore_cache):
    global main_id
    if id == None:
        return
    
    if not id.id_data is main_id: # prevent cross over onto other IDs. stay on one ID
        if isinstance(id.id_data, bpy.types.NodeTree): # material.node_tree, compositing node tree
            pass
        elif isinstance(id.id_data, bpy.types.Collection) and isinstance(main_id, bpy.types.Scene): # scene.collection
            pass
        else:
            return

    line=list(line)
    if id in line_data:
        return
    line_data = list(line_data)
    line_data.append(id)
    
    for attr_name, attr in sorted(id.bl_rna.properties.items(), key=lambda a: a[0]):
        current_attr = line + [attr_name]
        
        if subs.get(type(getattr(attr, 'fixed_type', None))):
            ignore_cache = True
        if (not attr_name in valid_paths.get(type(id).bl_rna, set())) and not ignore_cache:
            continue
        if any([attr_name in ignores.get(super, set()) for super in type(id).mro()]):
            continue
        
        if attr_name in {'rna_type', 'original'}: continue
        if attr.type == 'POINTER':
            the_pointer = getattr(id, attr_name)
            if attr.is_readonly:
                if the_pointer == target_id:
                    found(current_attr)
                    return
                starter(the_pointer, current_attr, line_data, target_id, ignore_cache)
            else:
                if the_pointer == target_id:
                    found(current_attr)
                    return
        if attr.type == 'COLLECTION':
            collection_items = getattr(id, attr_name)
            for n, item in enumerate(collection_items):
                #item_name = getattr(item, 'name', None)
                #iter_name = '"' + item_name + '"' if item_name else n
                iter_name = n
                if item == target_id:
                    found(current_attr + [f'[{iter_name}]'])
                    continue
                starter(item, current_attr + [f'[{iter_name}]'], line_data, target_id, ignore_cache)
    try:
        for key, value in list(id.items()):
            if getattr(id, key, None) == value:
                continue
            if value == target_id:
                found(line + [f'["{key}"]'])
            if isinstance(value, list):
                for n, item in enumerate(value):
                    if target_id is item:
                        found(line + [f'["{key}"][{n}]'])
            
    except:
        pass

#############