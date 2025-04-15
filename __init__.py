bl_info = {
    "name": "Quicke Mat",
    "author": "Mark",
    "version": (0, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar",
    "description": "A collection of tools: color, mirror, and more.",
    "category": "3D View",
}

from . import QuickieMaterial

def register():
    QuickieMaterial.register()

def unregister():
    QuickieMaterial.unregister()
