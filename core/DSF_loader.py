
from xplnedsf2 import *
import bpy
import os


def set_separator(filepath, to='/', double_backslash=False):
    """
    This library uses '/' as separator for directories in filenames.
    This functions sets this default separator or it sets it with to='os' to the one used by os.
    The updated filename is returned.
    """
    if to != 'os':  # so we are setting from os-separator to the one defined in to value
        return filepath.replace(os.sep, to)
    # if to = 'os' we set the separator of the os
    if os.sep == '\\' and double_backslash:
        return filepath.replace('/', '\\\\')  # double_backslash might be required if strings are exported further
    else:  # who knows what else could exist ;-)
        return filepath.replace('/', os.sep)


class DSF_loader:
    def __init__(self, wb, eb, sb, nb, scl, lp_overlay):

        self.AREA_W = wb  # define area from west to east and south to north to be extracted 
        self.AREA_E = eb  # 0 to 1 extracts the full one by on grid
        self.AREA_S = sb  # you could also use the full coordinates like 50.21 or -7.4
        self.AREA_N = nb
        
        self.SCALING = scl
        self.LAYER_PER_OVERLAY = lp_overlay  # if this is true each overlay terrain will be defined as individual object

        # Path to X-Plane.exe (use '/' delimiter), if not set here it is retrieved from dsf file loaded (under X-Plane)
        self.xp_path = ""
        self.dsf_file = ""  # this value is set when DSF_loader is executed

    def read_ter_file(self, ter_path):
        """
        Reads X-Plane terrain file (.ter) in ter_path and returns values as dictionary.
        In case of errors the dict contains key ERROR with value containing description of error.
        To read default terrains the path for X-Plane (self.xp_path) is needed.
        In order to read non default terrain the path of the dsf file (self.dsf_path) is needed.
        All filenames are using '/' as delimiter as in X-Plane definitions.
        """
        ter = dict()
        ter_file_id = ['A', '800', 'TERRAIN']  # each XP terrain file has these values in the first 3 lines

        if ter_path == 'terrain_Water':  # No terrain file for Water
            return ter

        if ter_path.startswith("lib/g10"):  # global XP 10 terrain definition
            filename = self.xp_path + "/Resources/default scenery/1000 world terrain" + ter_path[7:]  # remove lib/g10
        elif ter_path.startswith("terrain/"):  # local dsf terrain definition
            filename = self.dsf_file[:self.dsf_file.rfind("Earth nav data")] + ter_path  # remove part for dsf location
        else:
            ter["ERROR"] = "Unknown Terrain definition: " + ter_path
            return ter

        try:
            with open(set_separator(filename, to='os'), encoding="utf8") as f:
                for i, line in enumerate(f):
                    if i < 3:  # checking that the first three lines of the file include the ter_file_id
                        if line.strip() != ter_file_id[i]:
                            ter["ERROR"] = "Missing terrain file identifier " + ter_file_id[i] + " in line " + i + \
                                           "in terrain file: " + ter_path
                            return ter
                    values = line.split()
                    if len(values) > 0:  # skip empty line
                        key = values.pop(0)
                        if len(values) > 0 and values[0].startswith("../"):  # replace relative path with full path
                            filepath = filename[:filename.rfind("/")]  # get just path without name of file in path
                            values[0] = filepath[:filepath.rfind("/") + 1] + values[0][3:]
                        if key in ter:  # in case the key is used multiple times in ter file, just append add. values
                            ter[key] = ter[key].append(values)
                        else:
                            ter[key] = values
        except IOError:
            ter["ERROR"] = "Error reading terrain file: " + filename

        return ter

    def add_material(self, mat_name, ter, bpy):
        """
        Function adds new blender material (bpy needed) based on the X-Plane read terrain file information (ter).
        The material name (mat_name) is the terrain name in X-Plane with '_O' attached in case of Overlay terrain.
        The created material (m) in Blender is returned.
        """
        m = bpy.data.materials.new(mat_name)
        if mat_name.find('terrain_Water') < 0:  # this is no water
            if "BASE_TEX" in ter:
                tex_image_file = set_separator(ter["BASE_TEX"][0], to='os', double_backslash=True)
            elif "BASE_TEX_NOWRAP" in ter:
                tex_image_file = set_separator(ter["BASE_TEX_NOWRAP"][0], to='os', double_backslash=True)
            else:
                tex_image_file = "ERROR_No_BASE_TEX_definition_found_in_terrain_file"
            m.use_nodes = True
            bsdf = m.node_tree.nodes["Principled BSDF"]
            tex_image = m.node_tree.nodes.new('ShaderNodeTexImage')
            tex_image.location = (-400, 280)
            tex_image.image = bpy.data.images.load(tex_image_file, check_existing=True)
            m.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
            bsdf.inputs[7].default_value = 0.01  # This is setting the specular intensity
            ### TBD: increase roughness ###
            if mat_name.endswith("_O"):  # add border texture for overlay
                if "BORDER_TEX" in ter:
                    border_image_file = set_separator(ter["BORDER_TEX"][0], to='os', double_backslash=True)
                    border_image = m.node_tree.nodes.new('ShaderNodeTexImage')
                    border_image.location = (-400, 0)
                    border_image.image = bpy.data.images.load(border_image_file, check_existing=True)
                    border_image.image.colorspace_settings.name = 'Non-Color'
                    m.node_tree.links.new(bsdf.inputs['Alpha'], border_image.outputs['Color'])
                    m.blend_method = 'CLIP'
                    node = m.node_tree.nodes.new('ShaderNodeUVMap')
                    node.location = (-700, 0)
                    node.uv_map = "borderUV"
                    # add link from new uv map to image texture:
                    m.node_tree.links.new(node.outputs[0], border_image.inputs[0])
                else:
                    print("WARNING: No texture file found for this terrain overlay/material!\n")
                
        else:  # material definition for water
            tex_image_file = set_separator(self.xp_path + "/Resources/bitmaps/world/water/any.png", to='os',
                                           double_backslash=True)
            m.use_nodes = True
            bsdf = m.node_tree.nodes["Principled BSDF"]
            tex_image = m.node_tree.nodes.new('ShaderNodeTexImage')
            tex_image.image = bpy.data.images.load(tex_image_file, check_existing=True)
            m.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
            ### TBD: Change specular, roughness, transmission to good values for water ###
        return m
                
    def execute(self, dsf_filename):
        self.dsf_file = set_separator(dsf_filename)  # making sure that only '/' is used for delimiter in file path
        print("Reading DSF file: {}".format(self.dsf_file))
        if not len(self.xp_path):  # if path to X-Plane.exe is not defined, retrieve it from dsf file
            self.xp_path = self.dsf_file[:self.dsf_file.rfind("X-Plane 11") + 10]
            ######## TBD: Error if folder not found ############
            ######## TBD: Define X-Plane folder above as visible constant to be changed + Option to define path in import menu #############
        print("XP Path: {}".format(self.xp_path))

        dsf = XPLNEDSF()
        dsf.read(dsf_filename)  # read the filename in delivered with os-specific separator

        print("------------ Starting to transform DSF ------------------")
        grid_west = int(dsf.Properties["sim/west"])
        grid_south = int(dsf.Properties["sim/south"])
        print("Importing Mesh and setting west={} and south={} to origin.".format(grid_west, grid_south))
        if 0 <= self.AREA_W <= 1 and 0 <= self.AREA_S <= 1: 
            self.AREA_W += grid_west
            self.AREA_E += grid_west
            self.AREA_S += grid_south
            self.AREA_N += grid_south
        print("But extracting just from west {} to east {} and south {} to north {}".format(self.AREA_W, self.AREA_E,
                                                                                            self.AREA_S, self.AREA_N))

        # Load all terrain files that dsf file into a dictionary
        terrain_details = dict()  # containing per terrain index the details of .ter-file in dict
        for ter_id in dsf.DefTerrains:
            print("Loading Terrain {}".format(dsf.DefTerrains[ter_id]))
            terrain_details[ter_id] = self.read_ter_file(dsf.DefTerrains[ter_id])
            if "ERROR" in terrain_details[ter_id]:
                print(terrain_details[ter_id]["ERROR"])
        print("Loaded {} terrain details".format(len(terrain_details)))

        # SORT mesh patches so that pyhiscal mesh is bottom layer and all overlys are above
        # All layers sorted based on the flag and id of terrain in list, so that they will get higher z-value to avoid same z-layer artefacts
        # Also sort by near and far values to store them later in material name
        # In addition this sorting allows to switch materials with every layer
        ######## TBD: Give option to avoid loading of overlays
        ter_layers = dict()
        for p in dsf.Patches:
            #print("TerIndex {}:  Flag: {}  Near: {}   Far: {}".format(p.defIndex, p.flag, p.near, p.far))
            ter_type = (p.flag, p.defIndex, p.near, p.far)
            if ter_type in ter_layers:
                ter_layers[ter_type].append(p)
            else:
                ter_layers[ter_type] = [p]
        print("Sorted {} mesh patches into {} different types".format(len(dsf.Patches), len(ter_layers)))        
            
        verts = []
        edges = []  # will not be filled as Blender takes in case of empty edges the edges from the faces
        normals = []  # normals stored per vertex
        faces = [[]]
        uvs = [[]]
        uvs2 = [[]] # second uv coordinates given for borders in case of non projected mesh
        coords = dict()  # existing coordinates per object as key and index of them in verts as value
        tria_layer = dict()  # returning for a tria of vertex index the current layer (how many are above eahc ohter)
        materials = []  # list containing all information for all materials for all layers used
        matIndexPerTria = [[]] # list of material index for each tria of mesh
        used_materials = [[]]  # list containing for each layer the used materials

        for ter_layer_id in sorted(ter_layers.keys()):      
            projected_uv = ("PROJECTED" in terrain_details[ter_layer_id[1]]) # 2nd valud in ter_layer_id includes defintionIndex of patch
            water = (dsf.DefTerrains[ter_layer_id[1]] == "terrain_Water")
            if self.LAYER_PER_OVERLAY:
                if ter_layer_id[0] == 1:  # for basemesh we use layer 0
                    layer = 0
                else: 
                    layer += 1  # this requires that there was base-mesh before settin layer=0
            for p in ter_layers[ter_layer_id]:
                trias = p.triangles()
                
                if water and len(trias) and len(dsf.V[trias[0][0][0]][trias[0][0][1]]) <= 5:
                    projected_uv = True
                    ### TBD: create own material / ter_layer_id for projected Water to give it different name ###################
                    ##### or make sure that uv coordinates are outside [0:1] in case of projection
                else:
                    projected_uv = False
                # if water is projected depends if uv coordinates are given or not, taken from ferst vertex in first tria

                for t in trias:
                    if not (self.AREA_W <= dsf.V[t[0][0]][t[0][1]][0] <= self.AREA_E and self.AREA_S <= dsf.V[t[0][0]][t[0][1]][1] <= self.AREA_N)  \
                        and not (self.AREA_W <= dsf.V[t[1][0]][t[1][1]][0] <= self.AREA_E and self.AREA_S <= dsf.V[t[1][0]][t[1][1]][1] <= self.AREA_N) \
                        and not (self.AREA_W <= dsf.V[t[2][0]][t[2][1]][0] <= self.AREA_E and self.AREA_S <= dsf.V[t[2][0]][t[2][1]][1] <= self.AREA_N):
                            continue
                    ti = []  # index list of vertices of tria that will be added to faces
                    tuvs = []  # uvs for that triangle
                    tuvs2 = []  # 2nd uves for triangle e.g. for borders if existent
                    for v in t:  # this is now index to Pool and to vertex in Pool
                        #### TBD: Scale to Marcartor in order to have same east/west and north/south dimension #####
                        vx = round((dsf.V[v[0]][v[1]][0] - grid_west) * self.SCALING, 3)
                        vy = round((dsf.V[v[0]][v[1]][1] - grid_south) * self.SCALING, 3)
                        vz = dsf.getVertexElevation(dsf.V[v[0]][v[1]][0], dsf.V[v[0]][v[1]][1], dsf.V[v[0]][v[1]][2])
                        vz = round(vz / (100000/self.SCALING), 3)  ### TBD: Make stretching of height configureable
                        if (vx, vy) in coords:
                            vi = coords[(vx, vy)]
                            #### TBD: check if new normal is equal to existing one ###############
                        else:
                            vi = len(coords)  # index in verts is the last one, as coords will now be added
                            coords[(vx, vy)] = vi 
                            verts.append([vx, vy, vz])
                            nx = round(dsf.V[v[0]][v[1]][3], 4)  #### TBD: Rounding and if below can be removed; just checking if existent
                            ny = round(dsf.V[v[0]][v[1]][4], 4)
                            sqxy = nx*nx + ny*ny
                            if sqxy > 1:  # this should not happen for a normalized normal
                                print("Warning: This mesh inlcudes a not normalized normal. Just set it to straight up normal.")
                                sqxy = 1
                            normals.append([nx, ny, round(sqrt(1 - sqxy), 4)])
                            #if normals[-1] != [0.0, 0.0, 1.0]:
                            #    print(normals[-1])
                        ti.insert(0, vi)  # winding in Blender is just opposite as in X-Plane
                        if len(dsf.V[v[0]][v[1]]) == 7:  # in case of projection we need first uvs do by own unwrapping and use the others as second e.g. for border
                            if not projected_uv and p.flag == 1:  # for projected physical mesh; for overlay we would need second uvs for border
                                ########### TBD: when projected then map tuvs to vx and vy --> if NOT projected, CORRRECT ????????? ################################
                                tuvs.insert(0, (dsf.V[v[0]][v[1]][5], dsf.V[v[0]][v[1]][6]))
                                tuvs2.insert(0, (vx/100, vy/100))  # add this uv, even if not needed in order to get full uv-mesh for that layer
                            else:  # should only be the case if projected and we have overlay to get uv-map for border
                                tuvs.insert(0, (vx/100, vy/100))  #By this definition uvs exced [0;1] range, but should lead to scale 10 times the size
                                tuvs2.insert(0, (dsf.V[v[0]][v[1]][5], dsf.V[v[0]][v[1]][6]))  # uvs are defined for every vertex of every face / loop
                        elif len(dsf.V[v[0]][v[1]]) == 9: # first uvs for mesh 2nd for border
                            tuvs.insert(0, (dsf.V[v[0]][v[1]][5], dsf.V[v[0]][v[1]][6]))  # uvs are defined for every vertex of every face / loop
                            tuvs2.insert(0, (dsf.V[v[0]][v[1]][7], dsf.V[v[0]][v[1]][8]))  # uvs are defined for every vertex of every face / loop                    
                        else: # we don't have uvs so we unwrap our own ones
                            tuvs.insert(0, (vx/100, vy/100))  # By this definition uvs exced [0;1] range, but should lead to scale 10 times the size
                            tuvs2.insert(0, (vx/100, vy/100))  # Add uvs even if not needed for that tria but to have full uvs for that layer 
                    ### Identifiy layer for material ###
                    if not self.LAYER_PER_OVERLAY:
                        smallest_index = min(ti)  # make sure that smallest index is first in the list, but keep winding of tria
                        if smallest_index == ti[1]:
                            ti_match = (ti[1], ti[2], ti[0])  ########  CHANGING ORDER WOULD MEAN ALSO TO CHANG ORDER FOR UV --> created ti just for matching in dict !!!!!!! ##########
                        elif smallest_index == ti[2]:
                            ti_match = (ti[2], ti[0], ti[1])
                        else:
                            ti_match = (ti[0], ti[1], ti[2])
                        if ti_match in tria_layer:  # this tria is already existing
                            tria_layer[ti_match] += 1  # this new tria has to be pot on next layer
                            layer = tria_layer[ti_match]
                        else:
                            tria_layer[ti_match] = 0  # this is first tria which is layer 0 (base mesh)
                            layer = 0    
                    if layer >= len(faces):  # We need addtional layer so extend lists
                        faces.append([])
                        uvs.append([])
                        uvs2.append([])
                        matIndexPerTria.append([]) 
                        used_materials.append([])
                    faces[layer].append(ti)
                    uvs[layer].extend(tuvs)  # uvs added with correct order because of tria different winding
                    if tuvs2 != []:
                        uvs2[layer].extend(tuvs2)
                    if len(materials) == 0 or ter_layer_id != materials[-1]: # as materials are already sorted just check if this ter_layer_id is already at the end of materials
                        materials.append(ter_layer_id)
                    mat_id = len(materials) - 1     
                    if len(used_materials[layer]) == 0 or mat_id != used_materials[layer][-1]:  # as materials are sorted per layer_id we need just to check if required material is at end of the list
                        used_materials[layer].append(mat_id)
                    matIndexPerTria[layer].append(len(used_materials[layer]) - 1)  

        print("Arranged mesh into {} layers with {} materials".format(len(faces), len(materials)))
                        
        ### Create materials ###
        created_materials = []  # list containg references to all created blender materials
        for ter_layer_id in materials:
            terrain_name = str(ter_layer_id[1]) + '_'  # include terrain defintion index to allow correct sorting for a later import
            terrain_name += dsf.DefTerrains[ter_layer_id[1]]  # add name of terrain
            terrain_name = terrain_name + "_" + str(ter_layer_id[2]) + "_" + str(ter_layer_id[3])  # add near and far values for a later import
            ######### IDEA: STORE VALUES in material properties or special nodes ###########################
            if "PROJECTED" in terrain_details[ter_layer_id[1]]:
                terrain_name += "_P"  # add if base mesh is projected 
            if ter_layer_id[0] > 1:  # this is an overlay
                terrain_name += "_O"
            m = self.add_material(terrain_name, terrain_details[ter_layer_id[1]], bpy)  # add material to Blender materials
            created_materials.append(m)
                
        print("Created {} materials".format(len(created_materials)))        

        # Create own collection for basemesh and overlays
        main_collection = bpy.data.collections.new("XPDSF")
        bpy.context.scene.collection.children.link(main_collection)
        ol_collection = bpy.data.collections.new("Overlays")
        main_collection.children.link(ol_collection)


        for layer in range(len(faces)):
            if layer == 0:
                mesh_name = "Basemesh"
            else:
                mesh_name = "Overlay_" + str(layer)
                ### TBD Group overlays in own group
            mesh = bpy.data.meshes.new(mesh_name)  # add the new mesh

            obj = bpy.data.objects.new(mesh.name, mesh)
            
            if mesh_name.startswith("Base"):
                col = bpy.data.collections.get("XPDSF")
            else:
                col = bpy.data.collections.get("Overlays")
                
            col.objects.link(obj)
            bpy.context.view_layer.objects.active = obj

            ##### Delete loose vertices #### 
            if layer > 0:
                verts_layer = []
                faces_layer = []
                normals_layer = []
                verts_index = dict()
                for t in faces[layer]:
                    faces_layer.append([])
                    for v in t:
                        if v in verts_index:
                            faces_layer[-1].append(verts_index[v])
                        else:
                            verts_layer.append(verts[v])
                            normals_layer.append(normals[v])
                            verts_index[v] = len(verts_layer) - 1
                            faces_layer[-1].append(len(verts_layer) - 1)
            else:
                verts_layer = verts
                faces_layer = faces[layer]
                normals_layer = normals    #faces[layer] = []  # free memory (if this helps) ...

            mesh.from_pydata(verts_layer, edges, faces_layer)
            mesh.use_auto_smooth = True  # needed to make use of imported normals split
            #mesh.normals_split_custom_set([(0, 0, 0) for l in mesh.loops])
            mesh.normals_split_custom_set_from_vertices(normals_layer)  # set imported normals as custom split vertex normals    

            # ADDING MATERIALS PER LAYER
            for m in used_materials[layer]:
                bpy.context.object.data.materials.append(created_materials[m])

            for i, tria in enumerate(bpy.context.object.data.polygons):  #### Use obj instead of context ??
                tria.material_index = matIndexPerTria[layer][i]


            new_uv = bpy.context.active_object.data.uv_layers.new(name='baseUV')  #### Use obj instead of context ??
            for loop in bpy.context.active_object.data.loops:
                new_uv.data[loop.index].uv = uvs[layer][loop.index]
            bpy.context.object.data.uv_layers["baseUV"].active_render = True


            ######## ADDING BORDER UVS ###########
            if layer > 0:  # we haver overlay
                border_uv = bpy.context.active_object.data.uv_layers.new(name='borderUV')  #### Use obj instead of context ??
                for loop in bpy.context.active_object.data.loops:
                    border_uv.data[loop.index].uv = uvs2[layer][loop.index]

            ### Move overlays along z-axis
            obj.location.z += layer * 0.01
            
        return {"FINISHED"}

