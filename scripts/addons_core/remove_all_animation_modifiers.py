bl_info = {
    "name": "Remove All Animation Modifiers",
    "author": "Joseph Hansen",
    "version": (1,0,0),
    "blender": (4,2,0),
    "category":"Animation",
}
import bpy 

class RemoveAllModifiers(bpy.types.Operator):
    """Remove all modifiers from all animation curves"""
    bl_idname = "motbtools.remove_modifiers"
    bl_label = "Remove All Animation Modifiers"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for a in bpy.data.actions:
            for v in a.fcurves:
                for m in v.modifiers:
                    v.modifiers.remove(m)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(RemoveAllModifiers.bl_idname, text=RemoveAllModifiers.bl_label)

def register():
    bpy.utils.register_class(RemoveAllModifiers)
    bpy.types.GRAPH_MT_channel.append(menu_func)


def unregister():
    bpy.utils.unregister_class(RemoveAllModifiers)
    bpy.types.GRAPH_MT_channel.remove(menu_func)


if __name__ == "__main__":
    register()