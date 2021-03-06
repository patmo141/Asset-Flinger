'''
Copyright (C) 2014 Blender Aid
http://www.blendearaid.com
blenderaid@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import os, sys
import time

def generate():

    print (sys.argv)
    dragAndDropFilename = ""
    i = 0
    for arg in sys.argv:
        if arg == "--objFiles":
            dragAndDropFilename = sys.argv[i + 1]
        i = i + 1

    print ("Starting to generate " + dragAndDropFilename)
    files = []
    sceneDirectory = os.path.split(bpy.data.filepath)[0]
    if dragAndDropFilename == "":
        files = os.listdir(sceneDirectory)
        objFilename = None
        objFiles=[os.path.join(sceneDirectory,filename) for filename in files if ".obj" in filename]
    else:
        if os.path.isdir(dragAndDropFilename):
            sceneDirectory = dragAndDropFilename
            files = os.listdir(sceneDirectory)
            objFilename = None
            objFiles=[os.path.join(sceneDirectory,filename) for filename in files if ".obj" in filename]
        else:
            print (dragAndDropFilename)
            objFiles=[dragAndDropFilename]

    """
    for filename in files:
        if ".obj" in filename:
            objFilename = filename
            break
    """

    if len(objFiles) == 0:
        print ("No objects found!")

    for filename in objFiles:
        objFilename = filename

        if objFilename != None:
            bpy.ops.import_scene.obj(filepath=objFilename)


        for obj in bpy.context.selected_objects:
            obj.name = "OBJ"
        OBJ = bpy.data.objects["OBJ"]
        bpy.context.scene.objects.active = bpy.data.objects["OBJ"]
        bpy.ops.object.join()
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # Determine OBJ dimensions
        maxDimension = 1.0
        scaleFactor = maxDimension / max(OBJ.dimensions)

        # Scale uniformly
        OBJ.scale = (scaleFactor,scaleFactor,scaleFactor)

        # Center pivot
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')

        # Move object to origin
        bpy.ops.object.location_clear()

        # Move mesh up by half of Z dimension
        dimX = OBJ.dimensions[0]/2
        dimY = OBJ.dimensions[1]/2
        dimZ = OBJ.dimensions[2]/2
        OBJ.location = (0,0,dimZ)

        # Manual adjustments to CAMERAS
        CAMERAS = bpy.data.objects["cameras"]
        scalevalue = 1
        camScale = 0.5+(dimX*scalevalue+dimY*scalevalue+dimZ*scalevalue)/3
        CAMERAS.scale = (camScale,camScale,camScale)
        CAMERAS.location = (0,0,dimZ)

        # Make smooth, add SubSurf modifier and increase subdivisions
        bpy.ops.object.shade_smooth()
        bpy.ops.object.modifier_add(type='SUBSURF')
        OBJ.modifiers["Subsurf"].levels = 3

        # Apply SubSurf modifier
        # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

        # Assign existing METAL material to OBJ (Commented out to preserve the .OBJ material colors that are defined in the optional .MTL file)
        # METAL = bpy.data.materials['metal']
        # bpy.context.active_object.active_material = METAL

        # Render thumbnail
        thumbname = bpy.path.basename(bpy.data.filepath)
        thumbname = os.path.splitext(filename)[0]

        if thumbname:
            bpy.context.scene.render.filepath = os.path.join(sceneDirectory, thumbname)

        bpy.ops.render.render(write_still=True)

        # Delete OBJ and start over for other .obj's
        bpy.ops.object.delete()
