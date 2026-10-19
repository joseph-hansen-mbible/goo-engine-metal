bl_info = {
    "name": "Seams around selection",
    "description": "Create a seam running around selected faces. Removes other seams from selected area.",
    "author": "Wingcutangel",
    "blender": (2, 80, 0),
    "version": (1, 1),
    "location": "View3D > UV",
    "support": "COMMUNITY",
    "category": "UV",
}
import bpy


def main(context):
    bpy.ops.mesh.mark_seam(clear=True)
    bpy.ops.mesh.region_to_loop()
    bpy.ops.mesh.mark_seam(clear=False)
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')


class SeamsAroundSelection(bpy.types.Operator):
    """Create a seam around selected faces"""
    bl_idname = "object.seam_around_selection"
    bl_label = "Seams Around Selection"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None) and (context.tool_settings.mesh_select_mode[2] == True)

    def execute(self, context):
        main(context)
        return {'FINISHED'}

def draw_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(SeamsAroundSelection.bl_idname)

def register():
    bpy.utils.register_class(SeamsAroundSelection)
    bpy.types.VIEW3D_MT_uv_map.append(draw_func)


def unregister():
    bpy.utils.unregister_class(SeamsAroundSelection)
    bpy.types.VIEW3D_MT_uv_map.remove(draw_func)


if __name__ == "__main__":
    register()