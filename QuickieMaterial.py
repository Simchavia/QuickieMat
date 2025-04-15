import bpy
import os
from bpy.props import FloatVectorProperty, BoolProperty, EnumProperty

addon_idname = __package__

class VIEW3D_OT_quick_material_modal(bpy.types.Operator):
    bl_idname = "view3d.quick_material_modal"
    bl_label = "Quick Material Creator (Live)"
    bl_options = {'REGISTER', 'UNDO'}

    color: FloatVectorProperty(
        name="Viewport Color",
        subtype='COLOR',
        default=(0.8, 0.8, 0.8),
        min=0.0, max=1.0
    )

    def execute(self, context):
        return {'FINISHED'}

    def check(self, context):
        self.update_color(context)
        return True

    def update_color(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            return

        mesh = obj.data
        color = self.color

        if not mesh.materials:
            mat = bpy.data.materials.new(name=obj.name + "_01")
            mesh.materials.append(mat)
        else:
            mat = mesh.materials[0]
        mat.use_nodes = False
        mat.diffuse_color = (*color, 1.0)

        if "Col" not in mesh.color_attributes:
            mesh.color_attributes.new(name="Col", type='BYTE_COLOR', domain='CORNER')
        color_layer = mesh.color_attributes["Col"]

        group_name = "QuickColor"
        vg = obj.vertex_groups.get(group_name)
        if not vg:
            vg = obj.vertex_groups.new(name=group_name)
        brightness = sum(color) / 3
        vg.add(range(len(mesh.vertices)), brightness, 'REPLACE')

        was_in_mode = obj.mode
        if was_in_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                color_layer.data[loop_index].color = (*color, 1.0)

        mesh.update()

        if was_in_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode=was_in_mode)

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

    def draw(self, context):
        self.layout.prop(self, "color")

    def invoke(self, context, event):
        obj = context.active_object
        if obj and obj.data.materials:
            self.color = obj.data.materials[0].diffuse_color[:3]
        return context.window_manager.invoke_props_popup(self, event)

addon_keymaps = []

def update_keymap():
    unregister_keymap()
    prefs_entry = bpy.context.preferences.addons.get(addon_idname)
    if not prefs_entry or not prefs_entry.preferences.enable_hotkey:
        return
    prefs = prefs_entry.preferences
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            VIEW3D_OT_quick_material_modal.bl_idname,
            type=prefs.key_type,
            value='PRESS',
            ctrl=prefs.ctrl,
            shift=prefs.shift,
            alt=prefs.alt
        )
        addon_keymaps.append((km, kmi))

def unregister_keymap():
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except:
            pass
    addon_keymaps.clear()

class QuickViewportColorPreferences(bpy.types.AddonPreferences):
    bl_idname = addon_idname

    enable_hotkey: BoolProperty(
        name="Enable Hotkey",
        default=True,
        update=lambda self, ctx: update_keymap()
    )

    key_type: EnumProperty(
        name="Key",
        items=[
            ('ONE', '1', ''),
            ('TWO', '2', ''),
            ('THREE', '3', ''),
            ('FOUR', '4', ''),
            ('FIVE', '5', ''),
            ('Q', 'Q', ''),
            ('W', 'W', ''),
            ('E', 'E', ''),
            ('R', 'R', ''),
            ('A', 'A', ''),
            ('S', 'S', ''),
            ('D', 'D', ''),
            ('F', 'F', ''),
        ],
        default='ONE',
        update=lambda self, ctx: update_keymap()
    )

    ctrl: BoolProperty(name="Ctrl", default=True, update=lambda self, ctx: update_keymap())
    shift: BoolProperty(name="Shift", default=True, update=lambda self, ctx: update_keymap())
    alt: BoolProperty(name="Alt", default=False, update=lambda self, ctx: update_keymap())

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "enable_hotkey")
        layout.label(text="Hotkey")
        row = layout.row()
        row.prop(self, "ctrl", toggle=True)
        row.prop(self, "shift", toggle=True)
        row.prop(self, "alt", toggle=True)
        layout.prop(self, "key_type")

class VIEW3D_PT_quick_material_panel(bpy.types.Panel):
    bl_label = "Quicke Mat"
    bl_category = "Quicke Mat"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        prefs_entry = bpy.context.preferences.addons.get(addon_idname)
        if not prefs_entry:
            layout.label(text="(Add-on not registered)")
            return
        prefs = prefs_entry.preferences

        layout.label(text="Quicke Mat")
        layout.operator("view3d.quick_material_modal", text="Edit Material")
        layout.prop(prefs, "enable_hotkey", text="Enable Hotkey")
        layout.label(text="Hotkey Setup:")
        row = layout.row()
        row.prop(prefs, "ctrl", toggle=True)
        row.prop(prefs, "shift", toggle=True)
        row.prop(prefs, "alt", toggle=True)
        layout.prop(prefs, "key_type")

classes = (
    VIEW3D_OT_quick_material_modal,
    QuickViewportColorPreferences,
    VIEW3D_PT_quick_material_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    update_keymap()

def unregister():
    unregister_keymap()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
