bl_info = {
    "name": "Select All Keyframes Only On Selected Channel",
    "author": "Joseph Hansen",
    "version": (1, 0, 1),
    "blender": (4, 2, 0),
    "category": "Animation",
}

import bpy


class GRAPH_OT_select_all_keyframes_selected_channel(bpy.types.Operator):
    """Select all keyframes only on currently selected channel"""
    bl_idname = "motbtools.select_all_keyframes_selected_channel"
    bl_label = "Select All Keyframes on Selected Channel"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.space_data is not None
            and context.space_data.type == 'GRAPH_EDITOR'
        )

    def execute(self, context):
        bpy.ops.graph.select_all(action='DESELECT')
        bpy.ops.graph.hide(unselected=True)
        bpy.ops.graph.select_all(action='SELECT')
        bpy.ops.graph.reveal()
        return {'FINISHED'}


def draw_menu_item(self, context):
    self.layout.operator(
        GRAPH_OT_select_all_keyframes_selected_channel.bl_idname,
        text="All Keyframes on Selected Channels",
    )


addon_keymaps = []


def register():
    bpy.utils.register_class(GRAPH_OT_select_all_keyframes_selected_channel)
    bpy.types.GRAPH_MT_select.append(draw_menu_item)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Graph Editor", space_type='GRAPH_EDITOR')
        kmi = km.keymap_items.new(
            GRAPH_OT_select_all_keyframes_selected_channel.bl_idname,
            type='A',
            value='PRESS',
            shift=True,
        )
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.GRAPH_MT_select.remove(draw_menu_item)
    bpy.utils.unregister_class(GRAPH_OT_select_all_keyframes_selected_channel)


if __name__ == "__main__":
    register()