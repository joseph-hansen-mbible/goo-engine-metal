bl_info = {
    "name": "Linked Scenes Helper",
    "author": "Joseph Hansen",
    "version": (1,0,23),
    "blender": (4,2,0),
    "category":"Project Management",
}
import shutil
import bpy
import os
from glob import glob

def update_paths(self, context):
    pass

def network_path_connected():
    if not os.path.exists(bpy.context.scene.linked_scene_props.network_path):
        return "UNLINKED"
    else:
        return "NONE"

def append_log(message):
    props = bpy.context.scene.linked_scene_props
    if props.log_text:
        props.log_text = props.log_text + "\n" + message
    else:
        props.log_text = message

class ReloadAllLinkedScenes(bpy.types.Operator):
    bl_idname = "linkedscenes.reload_all_linked_scenes"
    bl_label = "Reload Linked Scenes"
    
    @classmethod
    def poll(cls, context):
        return os.path.exists(bpy.context.scene.linked_scene_props.network_path) and os.path.exists(bpy.context.scene.linked_scene_props.template_path)
    
    def execute(self, context):
        reloaded = []
        for k in bpy.data.scenes.keys():
            if bpy.data.scenes[k].library != None:
                bpy.data.scenes[k].library.reload()
                reloaded.append(k)
        
        append_log("--- Reload All Linked Scenes ---")
        if reloaded:
            for name in reloaded:
                append_log("  Reloaded: " + name)
        else:
            append_log("  No linked scenes found to reload.")
        
        return {'FINISHED'}

class ReloadLinkedScenesIncremental(bpy.types.Operator):
    # get the library paths for each, then iterate over PATH* to find the newest "_XX"
    # if there's no "_XX", still find the highest "_XX"
    # relocate
    bl_idname = "linkedscenes.reload_all_linked_scenes_incremental"
    bl_label = "Relocate Linked By Incremental"
    
    @classmethod
    def poll(cls, context):
        return os.path.exists(bpy.context.scene.linked_scene_props.network_path) and os.path.exists(bpy.context.scene.linked_scene_props.template_path)
    
    def execute(self, context):
        g = os.path.sep.join(bpy.data.filepath.split(os.path.sep)[:-1]) + os.path.sep + "*.blend"
        print ("g " + g)
        # i.e. '/Volumes/KidsExperience/Linked Scenes Test/*.blend'
        globbed = glob(g)
        
        append_log("--- Relocate Linked By Incremental ---")
        
        for k in bpy.data.scenes.keys():
            if bpy.data.scenes[k].library != None:
                current = bpy.data.scenes[k].library.filepath # i.e. '//Funky Sheep_02.blend', which is actually at '/Volumes/KidsExperience/Linked Scenes Test/Funky Sheep_02.blend'
                
                if current.startswith("//"):
                    current = current[2:]
                elif current.startswith(os.path.sep):
                    current = current[1:]
                    if current.startswith(os.path.sep):
                        current = current[1:]
                        
                print("Current " + current)
                
                current_glob = ""
                
                for h in globbed:
                    if h.endswith(current):
                        current_glob = h
                        print("current_glob " + current_glob)
                        break
                
                if current_glob != "":
                    # see if there's anything in globbed that is current_glob but _0M is _0N or _0O or _0P
                    current_glob_just_name = os.path.splitext(current_glob.split(os.path.sep)[-1])[0]
                    print ("current_glob_just_name "+current_glob_just_name)
                    
                    # Strip any existing _XX increment suffix to get the base name for matching
                    if "_" in current_glob_just_name:
                        try:
                            suffix = current_glob_just_name.split("_")[-1]
                            int(suffix[:2])  # confirm it looks like an increment
                            base_name = "_".join(current_glob_just_name.split("_")[:-1])
                        except ValueError:
                            base_name = current_glob_just_name
                    else:
                        base_name = current_glob_just_name
                    
                    print("base_name " + base_name)
                    
                    big_wigglers = []
                    biggest_wiggler = ""
                    biggest_wiggler_size = -1
                    
                    for i in globbed:
                        print("i" + i)
                        
                        i_name = os.path.splitext(i.split(os.path.sep)[-1])[0]
                        # Match files that are exactly the base name, or base name followed by _XX
                        if i_name == base_name or (i_name.startswith(base_name + "_") and i_name[len(base_name)+1:len(base_name)+3].isdigit()):
                            big_wigglers.append(i)
                    
                    for wiggler in big_wigglers:
                        try:
                            wiggler_name = os.path.splitext(wiggler.split(os.path.sep)[-1])[0]
                            if "_" not in wiggler_name or wiggler_name == base_name:
                                how_wiggly = 0
                            else:
                                how_wiggly = int(wiggler_name.split("_")[-1][:2])
                            
                            print(how_wiggly)
                            if how_wiggly > biggest_wiggler_size:
                                biggest_wiggler = wiggler
                                biggest_wiggler_size = how_wiggly
                        except:
                            # The non-incremented file doesn't have a [1]
                            print("Failed to find the biggest wiggler for " + current_glob_just_name)
                            pass
                    
                    print("biggest wiggler " + biggest_wiggler)
                    
                    if biggest_wiggler != "":
                        old_path = bpy.data.scenes[k].library.filepath
                        bpy.data.scenes[k].library.filepath = biggest_wiggler
                        bpy.data.scenes[k].library.reload()
                        append_log("  Relocated: " + k)
                        append_log("    From: " + old_path)
                        append_log("    To:   " + biggest_wiggler)
                    else:
                        append_log("  No increment found for: " + k + " (" + current + ")")
                else:
                    append_log("  Could not resolve path for: " + k + " (" + current + ")")
        
        return {'FINISHED'}
                
                        
class CreateMasterFile(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "linkedscenes.create_master_file"
    bl_label = "Go to Master File"

    @classmethod
    def poll(cls, context):
        return os.path.exists(bpy.context.scene.linked_scene_props.network_path) and os.path.exists(bpy.context.scene.linked_scene_props.template_path)
    
    def execute(self, context):
        project_folder = bpy.context.scene.linked_scene_props.network_path + os.path.sep + "Scene " + str(bpy.context.scene.linked_scene_props.scene_number) + os.path.sep + "Shot " + bpy.context.scene.linked_scene_props.shot_name
        if not os.path.exists(project_folder):
            shutil.copytree(bpy.context.scene.linked_scene_props.template_path, project_folder, dirs_exist_ok=True)
            bpy.ops.wm.open_mainfile(filepath=project_folder+os.path.sep+bpy.context.scene.linked_scene_props.template_filename)
        else:
            # already exists, so just open
            bpy.ops.wm.open_mainfile(filepath=project_folder+os.path.sep+bpy.context.scene.linked_scene_props.template_filename)

        return {'FINISHED'}


class ListMissingLinkedScenes(bpy.types.Operator):
    bl_idname = "linkedscenes.list_missing_linked_scenes"
    bl_label = "List Missing Linked Scenes"

    def execute(self, context):
        append_log("--- Missing Linked Scenes ---")
        missing = []

        for k in bpy.data.scenes.keys():
            scene = bpy.data.scenes[k]
            if scene.library is not None:
                filepath = scene.library.filepath
                # Resolve relative path
                abs_path = bpy.path.abspath(filepath)
                if not os.path.exists(abs_path):
                    missing.append((k, abs_path))

        if missing:
            for name, path in missing:
                append_log("  MISSING: " + name)
                append_log("    Path: " + path)
        else:
            append_log("  All linked scenes resolved successfully.")

        return {'FINISHED'}


class ClearLinkedScenesLog(bpy.types.Operator):
    bl_idname = "linkedscenes.clear_log"
    bl_label = "Clear Log"

    def execute(self, context):
        context.scene.linked_scene_props.log_text = ""
        return {'FINISHED'}


class CopyLinkedScenesLog(bpy.types.Operator):
    bl_idname = "linkedscenes.copy_log"
    bl_label = "Copy Log"

    def execute(self, context):
        log = context.scene.linked_scene_props.log_text
        if log:
            context.window_manager.clipboard = log
            self.report({'INFO'}, "Log copied to clipboard.")
        else:
            self.report({'WARNING'}, "Log is empty.")
        return {'FINISHED'}


class LinkedSceneProperties(bpy.types.PropertyGroup):
    network_path: bpy.props.StringProperty(name="Network Path", update=update_paths, subtype="DIR_PATH")
    project_name: bpy.props.StringProperty(name="Project Name", update=update_paths)
    scene_number: bpy.props.IntProperty(name="Scene Number", update=update_paths)
    shot_name: bpy.props.StringProperty(name="Shot Name", update=update_paths, maxlen=3)
    template_path: bpy.props.StringProperty(name="Template Folder", default="/Volumes/KidsExperience/Linked Scenes Template - Do Not Delete", subtype="DIR_PATH")
    template_filename: bpy.props.StringProperty(name="Template File Name", default = "master file.blend")
    log_text: bpy.props.StringProperty(name="Log", default="")


class LinkedScenesPanel(bpy.types.Panel):
    bl_label = "Linked Scenes"
    bl_idname = "OBJECT_PT_linkedscenes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        (panel_label, panel) = layout.panel("linkedscenes_settings", default_closed=True)
        panel_label.label(text="Settings")
        column = layout.column()
        box = column.box().column()
        
        if panel:
            panel.label(text="Path to the project folder")
            panel.label(text="i.e. /Volumes/KidsExperience/Mary and The Nativity")
            row = panel.row(align=True)
            row.label(text="Network Path")
            row.prop(scene.linked_scene_props, "network_path", text="", icon=network_path_connected())
            row = panel.row(align=True)
            row.label(text="Path to the Master File Template")
            row.prop(scene.linked_scene_props, "template_path", text = "")
            panel.prop(scene.linked_scene_props, "template_filename")
            
        box.prop(scene.linked_scene_props, "scene_number")
        row = box.row(align=True)
        row.label(text="Shot Name (i.e. 1, 2A, 21B)")
        row.prop(scene.linked_scene_props, "shot_name", text="")
        box.operator("linkedscenes.create_master_file", icon="FILE_ALIAS")
        
        row = layout.row()
        row.operator("linkedscenes.reload_all_linked_scenes", icon="UV_SYNC_SELECT")
        row = layout.row()
        row.operator("linkedscenes.reload_all_linked_scenes_incremental", icon="ZOOM_ALL")

        # Collapsible log panel
        (log_label, log_panel) = layout.panel("linkedscenes_log", default_closed=False)
        log_label.label(text="Log")
        if log_panel:
            row = log_panel.row(align=True)
            row.operator("linkedscenes.list_missing_linked_scenes", icon="QUESTION")
            row = log_panel.row(align=True)
            row.operator("linkedscenes.copy_log", icon="COPYDOWN")
            row.operator("linkedscenes.clear_log", icon="TRASH")

            log_text = scene.linked_scene_props.log_text
            if log_text:
                box = log_panel.box()
                for line in log_text.split("\n"):
                    box.label(text=line)
            else:
                log_panel.label(text="No log entries yet.", icon="INFO")


def register():
    bpy.utils.register_class(LinkedSceneProperties)
    bpy.utils.register_class(LinkedScenesPanel)
    bpy.utils.register_class(CreateMasterFile)
    bpy.utils.register_class(ReloadAllLinkedScenes)
    bpy.utils.register_class(ReloadLinkedScenesIncremental)
    bpy.utils.register_class(ListMissingLinkedScenes)
    bpy.utils.register_class(ClearLinkedScenesLog)
    bpy.utils.register_class(CopyLinkedScenesLog)
    bpy.types.Scene.linked_scene_props = bpy.props.PointerProperty(type=LinkedSceneProperties)


def unregister():
    bpy.utils.unregister_class(LinkedSceneProperties)
    bpy.utils.unregister_class(LinkedScenesPanel)
    bpy.utils.unregister_class(CreateMasterFile)
    bpy.utils.unregister_class(ReloadAllLinkedScenes)
    bpy.utils.unregister_class(ReloadLinkedScenesIncremental)
    bpy.utils.unregister_class(ListMissingLinkedScenes)
    bpy.utils.unregister_class(ClearLinkedScenesLog)
    bpy.utils.unregister_class(CopyLinkedScenesLog)
    del bpy.types.Scene.linked_scene_props


if __name__ == "__main__":
    register()