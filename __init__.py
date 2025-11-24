bl_info = {
    "name" : 'ID Tools' ,
    "description" : "Quickly inspect the total size of datablocks",
    "author" : "hisanimations",
    "version" : (1, 1, 0),
    "blender" : (3, 0, 0),
    "location" : "Outliner > Context Menu > ID Tools",
    "support" : "COMMUNITY",
    "category" : "Import-Export",
    "doc_url": "https://github.com/hisprofile/datascale"
}

import bpy
import os
from bpy.types import (Operator, AddonPreferences, Menu, PropertyGroup)
from bpy.utils import register_classes_factory
from bpy.props import (BoolProperty, StringProperty, EnumProperty, PointerProperty)

floating_id: bpy.types.ID = None
exclude_id: bpy.types.ID = None
flag_YES = {'YES'}
flag_MAKE_LIST = {'MAKE_LIST'}

id_type_to_collection_name = {
    'ACTION': 'actions',
    'ARMATURE': 'armatures',
    'BRUSH': 'brushes',
    'CAMERA': 'cameras',
    'CACHEFILE': 'cache_files',
    'COLLECTION': 'collections',
    'CURVE': 'curves',
    'CURVES': 'curves',
    'FONT': 'fonts',
    'GREASEPENCIL': 'grease_pencils',
    'IMAGE': 'images',
    'KEY': 'shape_keys',
    'LATTICE': 'lattices',
    'LIBRARY': 'libraries',
    'LIGHT': 'lights',
    'LIGHT_PROBE': 'lightprobes',
    'LINESTYLE': 'linestyles',
    'MASK': 'masks',
    'MATERIAL': 'materials',
    'MESH': 'meshes',
    'META': 'metaballs',
    'MOVIECLIP': 'movieclips',
    'NODETREE': 'node_groups',
    'OBJECT': 'objects',
    'PAINTCURVE': 'paint_curves',
    'PALETTE': 'palettes',
    'PARTICLE': 'particles',
    'POINTCLOUD': 'pointclouds',
    'SCENE': 'scenes',
    'SCREEN': 'screens',
    'SOUND': 'sounds',
    'SPEAKER': 'speakers',
    'TEXT': 'texts',
    'TEXTURE': 'textures',
    'VOLUME': 'volumes',
    'WINDOWMANAGER': 'window_managers',
    'WORKSPACE': 'workspaces',
    'WORLD': 'worlds'
}

id_type_to_icon = {
    "ACTION": "ACTION",
    "ARMATURE": "ARMATURE_DATA",
    "BRUSH": "BRUSH_DATA",
    "CACHEFILE": "FILE",
    "CAMERA": "CAMERA_DATA",
    "COLLECTION": "OUTLINER_COLLECTION",
    "CURVE": "CURVE_DATA",
    "CURVES": "CURVES_DATA",
    "FONT": "FONT_DATA",
    "GREASEPENCIL": "GREASEPENCIL",
    "GREASEPENCIL_V3": "GREASEPENCIL",
    "IMAGE": "IMAGE_DATA",
    "KEY": "SHAPEKEY_DATA",
    "LATTICE": "LATTICE_DATA",
    "LIBRARY": "LIBRARY_DATA_DIRECT",
    "LIGHT": "LIGHT_DATA",
    "LIGHT_PROBE": "LIGHTPROBE_SPHERE",
    "LINESTYLE": "LINE_DATA",
    "MASK": "MOD_MASK",
    "MATERIAL": "MATERIAL_DATA",
    "MESH": "MESH_DATA",
    "META": "META_DATA",
    "MOVIECLIP": "TRACKER",
    "NODETREE": "NODETREE",
    "OBJECT": "OBJECT_DATA",
    "PAINTCURVE": "CURVE_BEZCURVE",
    "PALETTE": "COLOR",
    "PARTICLE": "PARTICLE_DATA",
    "POINTCLOUD": "POINTCLOUD_DATA",
    "SCENE": "SCENE_DATA",
    "SCREEN": "WORKSPACE",
    "SOUND": "SOUND",
    "SPEAKER": "SPEAKER",
    "TEXT": "TEXT",
    "TEXTURE": "TEXTURE_DATA",
    "VOLUME": "VOLUME_DATA",
    "WINDOWMANAGER": "WINDOW",
    "WORKSPACE": "WORKSPACE",
    "WORLD": "WORLD_DATA"
}

enum_id_items = [
    ('', 'ID Type', ''),
    ('ACTION', 'Action', '', 'ACTION', 0),
    ('ARMATURE', 'Armature', '', 'ARMATURE_DATA', 1),
    ('BRUSH', 'Brush', '', 'BRUSH_DATA', 2),
    ('CACHEFILE', 'Cache File', '', 'FILE', 3),
    ('CAMERA', 'Camera', '', 'CAMERA_DATA', 4),
    ('COLLECTION', 'Collection', '', 'OUTLINER_COLLECTION', 5),
    ('CURVE', 'Curve', '', 'CURVE_DATA', 6),
    ('CURVES', 'Curves', '', 'CURVES_DATA', 7),
    ('FONT', 'Font', '', 'FONT_DATA', 8),
    ('GREASEPENCIL', 'Grease Pencil', '', 'GREASEPENCIL', 9),
    ('IMAGE', 'Image', '', 'IMAGE_DATA', 11),
    ('KEY', 'Key', '', 'SHAPEKEY_DATA', 12),
    ('LATTICE', 'Lattice', '', 'LATTICE_DATA', 13),
    ('LIBRARY', 'Library', '', 'LIBRARY_DATA_DIRECT', 14),
    ('LIGHT', 'Light', '', 'LIGHT_DATA', 15),
    ('LIGHT_PROBE', 'Light Probe', '', 'LIGHTPROBE_SPHERE', 16),
    ('LINESTYLE', 'Line Style', '', 'LINE_DATA', 17),
    ('MASK', 'Mask', '', 'MOD_MASK', 18),
    ('MATERIAL', 'Material', '', 'MATERIAL_DATA', 19),
    ('', '', ''),
    ('MESH', 'Mesh', '', 'MESH_DATA', 20),
    ('META', 'Metaball', '', 'META_DATA', 21),
    ('MOVIECLIP', 'Movie Clip', '', 'TRACKER', 22),
    ('NODETREE', 'Node Tree', '', 'NODETREE', 23),
    ('OBJECT', 'Object', '', 'OBJECT_DATA', 24),
    ('PAINTCURVE', 'Paint Curve', '', 'CURVE_BEZCURVE', 25),
    ('PALETTE', 'Palette', '', 'COLOR', 26),
    ('PARTICLE', 'Particle', '', 'PARTICLE_DATA', 27),
    ('POINTCLOUD', 'Point Cloud', '', 'POINTCLOUD_DATA', 28),
    ('SCENE', 'Scene', '', 'SCENE_DATA', 29),
    ('SCREEN', 'Screen', '', 'WORKSPACE', 30),
    ('SOUND', 'Sound', '', 'SOUND', 31),
    ('SPEAKER', 'Speaker', '', 'SPEAKER', 32),
    ('TEXT', 'Text', '', 'TEXT', 33),
    ('TEXTURE', 'Texture', '', 'TEXTURE_DATA', 34),
    ('VOLUME', 'Volume', '', 'VOLUME_DATA', 35),
    ('WINDOWMANAGER', 'Window Manager', '', 'WINDOW', 36),
    ('WORKSPACE', 'Workspace', '', 'WORKSPACE', 37),
    ('WORLD', 'World', '', 'WORLD_DATA', 38)
]

if bpy.app.version < (5, 0, 0):
    id_type_to_collection_name['GREASEPENCIL_V3'] = 'grease_pencils_v3'
    enum_id_items.insert(11, ('GREASEPENCIL_V3', 'Grease Pencil v3', '', 'GREASEPENCIL', 10))

def return_ids(context) -> set[bpy.types.ID] | bpy.types.ID:
    if context.area.type in {'OUTLINER', 'VIEW_3D'}:
        return context.selected_ids
    elif getattr(context, 'id', None):
        return context.id
    elif context.area.type == 'PROPERTIES':
        space = context.space_data
        space_context = space.context
        match space_context:
            case 'OBJECT':
                return context.object
            case 'DATA':
                return context.object.data
            case 'MATERIAL':
                return context.material
            case 'SCENE':
                return context.scene
            case 'TEXTURE':
                return context.texture
            case 'WORLD':
                return context.world
            case 'COLLECTION':
                return context.collection
            case 'PARTICLES':
                return context.particle_settings
    return floating_id

def return_ids_set(context: bpy.types.Context, poll=False) -> set[bpy.types.ID]:
    gatherings = set()
    ids = return_ids(context)
    if '__iter__' in dir(ids):
        gatherings.update(set(ids))
    else:
        gatherings.add(ids)
    gatherings.discard(None)
    if not gatherings:
        return None
    return gatherings

def format_size(size_in_bytes):
    """
    Convert size in bytes to a human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def template_any_ID(layout: bpy.types.UILayout, data, property: str, type_property: str, text: str='', text_ctxt: str='', translate: bool=True) -> None:
    row = layout.row(align=True)
    row.alignment = 'EXPAND'
    sub = row.row(align=True)
    sub.alignment = 'LEFT'
    sub.prop(data, type_property, icon_only=False, text='')

    sub = row.row(align=True)
    sub.alignment = 'EXPAND'

    type_name = getattr(data, type_property)
    if type_name in id_type_to_collection_name:
        icon = data.bl_rna.properties[type_property].enum_items[type_name].icon
        sub.prop_search(data, property, bpy.data, id_type_to_collection_name[type_name], text='', icon=icon)

class id_tools_OT_weigh(Operator):
    bl_idname = 'id_tools.weigh'
    bl_label = 'Weigh IDs'
    bl_description = 'Export the IDs to calculate their total size on the hard drive.'

    @classmethod
    def poll(cls, context):
        return bool(return_ids(context))

    def execute(self, context):
        props = context.preferences.addons[__package__].preferences
        gatherings = return_ids_set(context)
        if not gatherings:
            return {'CANCELLED'}
        if bpy.app.version >= (4, 2, 0):
            temp_file = os.path.join(bpy.utils.extension_path_user(__package__, create=True), 'temp.blend')
        else:
            temp_file = os.path.join(os.path.dirname(__file__), 'temp.blend')
        bpy.data.libraries.write(temp_file, gatherings, compress=props.compress)
        file_size = os.path.getsize(temp_file)
        file_size = format_size(file_size)
        os.remove(temp_file)
        report_msg = ' '.join([
            'The',
            str(len(gatherings)),
            'datablocks' if len(gatherings) > 1 else 'datablock', # nice to pick between plural and singular
            'weigh' if len(gatherings) > 1 else 'weighs',
            file_size
        ])
        self.report({'INFO'}, report_msg)
        return {'FINISHED'}

class id_tools_OT_replace_id(Operator):
    bl_idname = 'id_tools.replace_id'
    bl_label = 'Replace ID'
    bl_description = 'Replace all instances of the selected ID with another ID'
    bl_options = {'UNDO'}
    
    was_invoked = False

    @classmethod
    def poll(cls, context):
        return len(return_ids_set(context)) == 1

    def invoke(self, context, event):
        self.was_invoked = True
        context.window_manager.id_tools_props.id = None
        return context.window_manager.invoke_props_dialog(self, width=400, title='Replace ID', confirm_text='Replace')

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences  
        self.was_invoked = False

        props = context.window_manager.id_tools_props
        if not props.id: return {'CANCELLED'}

        id: bpy.types.ID = return_ids_set(context).pop()
        if not prefs.replace_with_selected:
            id.user_remap(props.id)
        else:
            props.id.user_remap(id)

        return {'FINISHED'}


    def draw(self, context):
        global exclude_id

        prefs = context.preferences.addons[__package__].preferences
        props = context.window_manager.id_tools_props
        layout = self.layout

        id = return_ids_set(context)
        if not id:
            layout.label(text='Inavlid entry point for tool! Bad, or not allowed ID!')
            return None

        id = id.pop()
        exclude_id = id
        icon = id_type_to_icon[id.id_type]
        collection_property = id_type_to_collection_name[id.id_type]

        layout.label(text='Be careful to not corrupt data!', icon='ERROR')
        layout.prop(prefs, 'replace_with_selected')
        row = layout.row()
        row.alignment = 'LEFT'
        
        s1 = row.row()
        s1.alignment = 'LEFT'
        s2 = row.row()
        s2.alignment = 'LEFT'

        c1 = s1.column()
        c1.label(text='Old ID:')
        c1.label(text='New ID:')

        c2 = s2.column()
        if not prefs.replace_with_selected:
            c2.label(text=id.name, icon=icon)
            c2.prop_search(props, 'id', bpy.data, collection_property, text='', icon=icon)
        else:
            c2.prop_search(props, 'id', bpy.data, collection_property, text='', icon=icon)
            c2.label(text=id.name, icon=icon)

class id_tools_OT_export(Operator):
    bl_idname = 'id_tools.export'
    bl_label = 'Export Selected IDs as Library'
    bl_description = 'Export selected IDs to a new .blend file'

    directory: StringProperty(subtype='DIR_PATH')
    filepath: StringProperty(subtype='FILE_PATH')
    filename: StringProperty(subtype='FILE_NAME', default='.blend')
    check_existing: BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )
    filename_ext = '.blend'
    filter_blender: BoolProperty(default=True, options={'HIDDEN'})
    filter_folder: BoolProperty(default=True, options={'HIDDEN'})
    filter_blenlib: BoolProperty(default=True, options={'HIDDEN'})
    filter_glob:StringProperty(default='.blend', options={'HIDDEN'})

    path_remap: EnumProperty(
        items=(
            ('NONE', 'None', 'No path manipulation.'),
            ('RELATIVE', 'Relative', 'Remap paths that are already relative to the new location.'),
            ('RELATIVE_ALL', 'Relative All', 'Remap all paths to be relative to the new location (default)'),
            ('ABSOLUTE', 'Absolute', 'Make all paths absolute on writing.')
        ),
        name='Library Path Remap',
        description='The Remap operation for used .blend libraries in the export',
        default='RELATIVE_ALL'
    )
    fake_user: BoolProperty(default=True, name='Fake Users for IDs', description='Give Fake Users to IDs to ensure their persistence')
    compress: BoolProperty(default=False, name='Compress', description='Compress the export')
    create_default_scene:BoolProperty(default=True, name='Create Default Scene', description='Creates a default scene so the exported IDs show on first run. Otherwise, they will be hidden until you manually link them to a scene.')

    @classmethod
    def poll(cls, context):
        return bool(return_ids(context))

    def draw(self, context):
        layout = self.layout
        layout.label(text='Library Path Remap Operation')
        col = layout.column()
        col.prop(self, 'path_remap', expand=True)
        layout.separator()
        layout.prop(self, 'fake_user')
        layout.prop(self, 'compress')
        layout.prop(self, 'create_default_scene')

    def invoke(self, context, event):
        props = context.preferences.addons[__package__].preferences
        self.compress = props.compress
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def check(self, context):
        import os
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(os.path.splitext(filepath)[0], self.filename_ext)
        if self.filepath != filepath: # is it better to just always return True?
            self.filepath = filepath
            return True
        return False
    
    def execute(self, context):
        default_scene = None
        ids = return_ids_set(context)
        if not ids:
             return {'CANCELLED'}
        if self.create_default_scene:
            # if there already is a scene selected, we need to check if there are selected collections or objects that aren't linked to this scene.
            # gather selected scenes, collections, and objects
            existing_scenes = set(filter(lambda a: isinstance(a, bpy.types.Scene), ids))
            selected_objs = set(filter(lambda a: isinstance(a, bpy.types.Object), ids))
            selected_cols = set(filter(lambda a: isinstance(a, bpy.types.Collection), ids))

            # create sets to remove from the selected data
            selected_cols_objs = set()
            [selected_cols_objs.update(set(col.objects)) for col in selected_cols]
            scenes_collections = set()
            [scenes_collections.update(set(scn.collection.children_recursive)) for scn in existing_scenes]
            scenes_objects = set()
            [scenes_objects.update(set(scn.objects)) for scn in existing_scenes]

            # isolate all collections who are not a part of any selected scene.
            # isolate all objects who are not a part of any selected scene.
            # isolate all objects who are not a part of any selected collections.
            selected_cols.difference_update(set(scenes_collections))
            selected_objs.difference_update(scenes_objects)
            selected_objs.difference_update(selected_cols_objs)
            # get only the collections that do not have parents
            [selected_cols.discard(child) for col in list(selected_cols) for child in col.children_recursive]

            if selected_cols or selected_objs:
                default_scene = bpy.data.scenes.new('ID_TOOLS_scene')
                ids.add(default_scene)
            if selected_cols:
                [default_scene.collection.children.link(col) for col in selected_cols]
            if selected_objs:
                [default_scene.collection.objects.link(obj) for obj in selected_objs]

        bpy.data.libraries.write(self.filepath, ids, path_remap=self.path_remap, fake_user=self.fake_user, compress=self.compress)
        
        if default_scene:
            bpy.data.scenes.remove(default_scene)
        
        filesize = format_size(os.path.getsize(self.filepath))
        self.report({'INFO'}, f'Export successful with a size of {filesize}')
        return {'FINISHED'}

class id_tools_OT_id_quick_attach(Operator):
    bl_idname = 'id_tools.id_quick_attach'
    bl_label = 'Quick Parent to ID'
    bl_description = 'Quickly parent children ID(s) to a parent ID using custom properties, ensuring the children IDs are always attached to the parent'

    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if not hasattr(context, 'id'):
            return False
        if len(getattr(context, 'selected_ids', [])) < 2:
            return False
        return True

    def does_exist_prop(self, context):
        id = context.id
        prop = id.get('id_tools_attach', 'HAS_NO_PROP')
        return prop != 'HAS_NO_PROP'
    
    def can_add_to_existing(self, context):
        id: bpy.types.ID = context.id
        prop = id.get('id_tools_attach', 'HAS_NO_PROP')
        if isinstance(prop, list):
            return flag_YES
        if isinstance(prop, bpy.types.ID):
            return flag_MAKE_LIST
        return False

    def execute(self, context):
        host_id = getattr(context, 'id', None)
        if host_id is None:
            return {'CANCELLED'}
        parasitic_ids = return_ids_set(context)
        parasitic_ids.discard(host_id)
        parasitic_ids = list(parasitic_ids)
        if len(parasitic_ids) == 0:
            return {'CANCELLED'}

        can_add = self.can_add_to_existing(context)
        if bool(can_add):
            existing_ids = host_id.get('id_tools_attach')
            if can_add == flag_MAKE_LIST:
                existing_ids = [existing_ids]
            existing_ids.extend(parasitic_ids)
            host_id['id_tools_attach'] = existing_ids
            return {'FINISHED'}
        else:
            if len(parasitic_ids) == 1:
                host_id['id_tools_attach'] = parasitic_ids.pop()
            else:
                host_id['id_tools_attach'] = parasitic_ids
            return {'FINISHED'}

class id_tools_OT_id_attach(Operator):
    bl_idname = 'id_tools.id_attach'
    bl_label = 'Parent to ID'
    bl_description = 'Parent children ID(s) to a parent ID using custom properties, ensuring the children IDs are always attached to the parent'

    add_to_existing: BoolProperty(default=False, name='Add to Existing', description='Add to the existing property')

    was_invoked = False

    bl_options = {'UNDO'}
    
    def does_exist_prop(self, context):
        props = context.window_manager.id_tools_props
        if not props.id: return 'HAS_NO_PROP'
        prop = props.id.get(props.property, 'HAS_NO_PROP')
        return prop != 'HAS_NO_PROP'
    
    def can_add_to_existing(self, context):
        props = context.window_manager.id_tools_props
        if not props.id: return False
        prop = props.id.get(props.property, 'HAS_NO_PROP')
        if isinstance(prop, list):
            return flag_YES
        if isinstance(prop, bpy.types.ID):
            return flag_MAKE_LIST
        return False

    def invoke(self, context, event):
        self.was_invoked = True
        return context.window_manager.invoke_props_dialog(self, width=400, title='ID Attach', confirm_text='Attach')

    def execute(self, context):
        if not self.was_invoked:
            return self.invoke(context, None)
        
        self.was_invoked = False
        props = context.window_manager.id_tools_props
        if not props.id: return {'CANCELLED'}
        selected_ids = list(return_ids_set(context))
        can_append = self.can_add_to_existing(context)
        if self.does_exist_prop(context) and bool(can_append) and self.add_to_existing:
            if can_append is flag_MAKE_LIST:
                props.id[props.property] = [props.id[props.property]]
            props.id[props.property] += selected_ids
            return {'FINISHED'}
        if len(selected_ids) == 1:
            selected_ids = selected_ids.pop()
        props.id[props.property] = selected_ids
        return {'FINISHED'}


    def draw(self, context):
        does_exist = self.does_exist_prop(context)
        can_append = self.can_add_to_existing(context)
        props = context.window_manager.id_tools_props

        layout = self.layout
        alert = does_exist and not (bool(can_append) and self.add_to_existing) and bool(props.id)
        box = layout.box().column()
        box.label(text='Property:')
        row = box.row()
        row.prop(props, 'property', text='')
        row.alert = alert
        box.alert = alert

        box = layout.box().column()
        box.label(text='Parent Data-Block:')
        template_any_ID(box, props, 'id', 'id_type')
        
        box = layout.box().column()
        row = box.row()
        row.prop(self, 'add_to_existing')
        row.enabled = does_exist and bool(can_append)
        if alert:
            box.label(text='Will replace existing property!', icon='ERROR')

class id_tools_OT_id_remove_from_hosts(Operator):
    bl_idname = 'id_tools.id_remove_from_hosts'
    bl_label = 'Unparent Selected ID(s)'
    bl_description = 'Unparent selected IDs from possible parent IDs, by removing them from custom properties'

    def execute(self, context):
        ids = return_ids_set(context)
        hosts = set()
        [hosts.add(host) for id in ids for host in bpy.data.user_map(subset=[id])[id]]

        for host in hosts:
            if host.library: continue
            for prop, value in list(host.items()):
                if isinstance(value, bpy.types.ID):
                    if value in ids:
                        del host[prop]
                        continue
                elif isinstance(value, list):
                    for id in ids:
                        if not id in value: continue
                        value.remove(id)
                    if len(value) == 0:
                        del host[prop]
                    else:
                        host[prop] = value
                else:
                    continue
        return {'FINISHED'}

class id_tools_OT_parasite_remove(Operator):
    bl_idname = 'id_tools.parasite_remove'
    bl_label = 'Dump ID(s) from Selected Parent(s)'
    bl_description = 'Unparent all children IDs parented to selected IDs by removing them from custom properties'

    def execute(self, context):
        hosts = return_ids_set(context)
        for host in hosts:
            if host.library: continue
            for prop, value in list(host.items()):
                if isinstance(value, bpy.types.ID):
                    del host[prop]
                    continue
                elif isinstance(value, list):
                    for item in value:
                        if not isinstance(item, bpy.types.ID): continue
                        value.remove(item)
                    if len(value) == 0:
                        del host[prop]
                    else:
                        host[prop] = value
                else:
                    continue
        return {'FINISHED'}

class id_tools_OT_make_props_overridable(Operator):
    bl_idname = 'id_tools.make_props_overridable'
    bl_label = 'Make Properties Overridable'
    bl_description = 'Make all custom properties on this ID library overridable'

    def execute(self, context):
        ids = return_ids_set(context)
        if not ids: return {'CANCELLED'}
        for id in ids:
            if id.library: continue
            id: bpy.types.ID
            for prop in id.keys():
                id.property_overridable_library_set(f'["{prop}"]', True)
        return {'FINISHED'}

class id_tools_OT_path_report(Operator):
    bl_idname = 'id_tools.path_report'
    bl_label = 'User Path Report'
    bl_description = 'Experimental! Reports all paths where an ID is used into the console.'

    def execute(self, context):
        from . import id_tools_path_report
        ids = return_ids_set(context)
        print('----------------------')
        print('BEGINNING PATH REPORT!')
        for id in ids:
            print('SEARCHING FOR', repr(id))
            print('')
            for user in bpy.data.user_map()[id]:
                id_tools_path_report.main_id = user
                print('USER:', repr(user))
                id_tools_path_report.starter(user, [repr(user)], [], id, False)
                print()
        print('END REPORT!')
        print('-----------')
        self.report({'INFO'}, 'Read report in the console!')
        return {'FINISHED'}

class ID_TOOLS_MT_Menu(Menu):
    bl_label = 'ID Tools'
    bl_idname = 'ID_TOOLS_MT_Menu'

    def draw(self, context):
        props = context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.prop(props, 'compress')
        layout.operator('id_tools.weigh')
        layout.operator('id_tools.export')
        layout.operator('id_tools.replace_id')
        layout.separator()
        if context.area.type == 'OUTLINER':
            layout.operator('id_tools.id_quick_attach')
        layout.operator('id_tools.id_attach')
        layout.operator('id_tools.id_remove_from_hosts')
        layout.operator('id_tools.parasite_remove')
        layout.operator('id_tools.make_props_overridable')
        layout.separator()
        layout.operator('id_tools.path_report')

def menu_func(self, context):
    global floating_id
    if not hasattr(context, 'id'): return

    floating_id = context.id
    #if (not getattr(context, 'property', None)) and (context.area.type == 'PROPERTIES'): return # i cannot get it to show at the same level as "Mark as asset." 
    # according to this issue, https://projects.blender.org/blender/blender/issues/126006
    # the "Mark as asset" operator shows when bpy.context.id can be accessed. this does not seem to exist in Python :(
    # edit: it does exist, but not in the context i need it to
    
    self.layout.separator()
    self.layout.menu('ID_TOOLS_MT_Menu')

def export_menu(self, context):
    self.layout.operator('id_tools.export')

def object_menu(self, context):
    self.layout.separator()
    self.layout.operator('id_tools.weigh')
    self.layout.operator('id_tools.id_attach')
    self.layout.operator('id_tools.make_properties_overridable')
    self.layout.operator('id_tools.path_report')


class id_tools_prefs(AddonPreferences):
    bl_idname = __package__
    compress: BoolProperty(default=False, name='Compress', description='Did you know you can save .blend files in a compressed state?')
    replace_with_selected: BoolProperty(default=False, name='Replace With Selected', description='Instead of replacing the selected ID, replace another ID *with* the selected ID')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'compress', text='Compress Results')
        layout.label(text='Did you know you can save .blend projects in a compressed state?')
        layout.label(text='To make every .blend file save as compressed by default in the future, save your start-up file as compressed!')
        layout.separator()
        layout.label(text='Resulting sizes include .blend file headers and not raw data, which is usually negligible.')

class id_tools_props(PropertyGroup):
    def poll_id(self, item):
        return item != exclude_id
    def reset_id(self, context):
        self.id = None
    def update_prop(self, context):
        if self.property == '':
            self.property = 'id_tools_attach'

    id: PointerProperty(type=bpy.types.ID, poll=poll_id)
    property: StringProperty(default='id_tools_attach', description='Custom Property name to save the ID under', update=update_prop)
    id_type: EnumProperty(items=enum_id_items,
        name='ID Type',
        description='Type of data block to set values to',
        options={'SKIP_SAVE'},
        default='OBJECT',
        update=reset_id)

classes = [
    id_tools_prefs,
    id_tools_props,
    id_tools_OT_weigh,
    id_tools_OT_export,
    id_tools_OT_replace_id,
    id_tools_OT_id_quick_attach,
    id_tools_OT_id_attach,
    id_tools_OT_id_remove_from_hosts,
    id_tools_OT_parasite_remove,
    id_tools_OT_make_props_overridable,
    id_tools_OT_path_report,
    ID_TOOLS_MT_Menu
]

reg_classes, unreg_classes = register_classes_factory(classes)

def register():
    reg_classes()
    bpy.types.WindowManager.id_tools_props = PointerProperty(type=id_tools_props)
    bpy.types.OUTLINER_MT_context_menu.append(menu_func)
    bpy.types.OUTLINER_MT_object.append(menu_func)
    bpy.types.OUTLINER_MT_collection.append(menu_func)
    bpy.types.UI_MT_button_context_menu.append(menu_func)
    bpy.types.TOPBAR_MT_file_export.append(export_menu)
    bpy.types.VIEW3D_MT_object.append(object_menu)

def unregister():
    unreg_classes()
    del bpy.types.WindowManager.id_tools_props
    bpy.types.OUTLINER_MT_context_menu.remove(menu_func)
    bpy.types.OUTLINER_MT_object.remove(menu_func)
    bpy.types.OUTLINER_MT_collection.remove(menu_func)
    bpy.types.UI_MT_button_context_menu.remove(menu_func)
    bpy.types.TOPBAR_MT_file_export.remove(export_menu)
    bpy.types.VIEW3D_MT_object.remove(object_menu)