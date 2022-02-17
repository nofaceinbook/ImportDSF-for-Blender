# ******************************************************************************
#
# ImportDSF for Blender: Python script for Blender 
#                        that allows import of X-Plane DSF files
#
# For more details refer to GitHub: https://github.com/nofaceinbook/ImportDSF-for-Blender
#
# WARNING: This code is still under development and may still have some errors.
#
# Copyright (C) 2022 by schmax (Max Schmidt)
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR 
# A PARTICULAR PURPOSE.  
# ******************************************************************************

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty, FloatProperty
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .core.DSF_loader import DSF_loader


bl_info = {
    "name": "ImportDSF",
    "author": "schmax",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "File > Import",
    "description": "Import-Export OBJ, Import OBJ mesh, UV's, materials and textures",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}


class ImportDSF(Operator, ImportHelper):
    """Load a X-Plane mesh from dsf file"""
    bl_idname = "import_mesh.dsf"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import DSF"

    # ImportHelper mixin class uses this
    filename_ext = ".dsf"

    filter_glob: StringProperty(
        default="*.dsf",
        options={'HIDDEN'},
    )
    
    east_bound: FloatProperty(
        name="West bound",
        description="West boundary, relative to tile (e.g. 0.4) or absolute (-29.6) in degree "
                    "(0.0 for any west tile border)",
        min=-180.0, max=180.0,
        soft_min=0.0, soft_max=1.0,
        default=0.0,
    )
    
    west_bound: FloatProperty(
        name="East bound",
        description="East boundary, relative to tile (e.g. 0.6) or absolute (-29.4) in degree "
                    "(1.0 for any east tile border)",
        min=-180.0, max=180.0,
        soft_min=0.0, soft_max=1.0,
        default=1.0,
    )
    
    south_bound: FloatProperty(
        name="South bound",
        description="South boundary, relative to tile (e.g. 0.4) or absolute (50.4) in degree "
                    "(0.0 for any south tile border)",
        min=-90.0, max=90.0,
        soft_min=0.0, soft_max=1.0,
        default=0.0,
    )
    
    north_bound: FloatProperty(
        name="North bound",
        description="North boundary, relative to tile (e.g. 0.6) or absolute (50.6) in degree "
                    "(1.0 for any nord tile border)",
        min=-90.0, max=90.0,
        soft_min=0.0, soft_max=1.0,
        default=1.0,
    )

    scaling: IntProperty(
        name="Scaling",
        default=1000,
        description="Multiplier for degree tile",
        min=1,
        max=100000,
    )
    
    separate_overlays: BoolProperty(
        name="Overlay per Terrain Type",
        description="Create separate overlays per terrain type",
        default=False
    )

    def execute(self, context):
        """Executes the import process """
        importer = DSF_loader(self.east_bound, self.west_bound, self.south_bound, self.north_bound, self.scaling,
                              self.separate_overlays)
        return importer.execute(self.filepath)


def menu_func_import(self, context):
    self.layout.operator(ImportDSF.bl_idname, text="X-Plane DSF mesh (.dsf)")


def register():
    bpy.utils.register_class(ImportDSF)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ImportDSF)
    

if __name__ == "__main__":       
    register()
