"""
    PSK Importer for Maya - Version 0.1.0
    Copyright (C) 2018 Philip/Scobalula

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
"""
import os
import sys
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import pskUtil as psk

def CreateMenu():
    """ Creates Menu in Maya's Window """
    cmds.setParent(mel.eval("$temp1=$gMainWindow"))
    if cmds.control("PSKTool", exists=True):
        cmds.deleteUI("PSKTool", menu=True)
    menu = cmds.menu("PSKTool", label= "PSK Tools",tearOff=True)
    cmds.menuItem(label= "Import PSK File...", command=lambda x:SelectPSKFile())
    cmds.menuItem(divider=True)
    cmds.menuItem(
        label= "Reload Script",
        command=lambda x:Reload())

def Reload():
    """ Reloads PSK Script and Library """
    mel.eval("python(\"reload(pskMaya)\")")
    reload(psk)

def SelectPSKFile():
    psk_file = cmds.fileDialog2(
        fileFilter="PSK File (*.psk)",
        dialogStyle=2,
        fileMode=1)

    if not psk_file:
        return

    LoadPSKFile(psk_file[0])

def LoadPSKFile(filePath):
    """ Loads PSK Data into Maya """
    # Load PSK File
    pskfile = psk.UnrealPSK(filePath)
    mObj = OpenMaya.MFnSingleIndexedComponent().create(OpenMaya.MFn.kMeshVertComponent)
    # Maya Arrays/Data
    weightIndices = OpenMaya.MIntArray()
    # Create Joints
    joints = []
    mjoints = []
    mtransform = OpenMaya.MFnTransform()
    bone_group = mtransform.create()
    mtransform.setName("PSKJoints")
    for i, joint in enumerate(pskfile.bones):
        mbone = OpenMayaAnim.MFnIkJoint()
        if i == 0:
            bone = mbone.create(bone_group)
        else:
            bone = mbone.create(joints[joint.parent])
        mbone.setName(joint.name)
        mbone.setOrientation(OpenMaya.MQuaternion(
            -joint.rotation[0],
            -joint.rotation[1],
            -joint.rotation[2],
            joint.rotation[3]))
        mbone.setTranslation(OpenMaya.MVector(
            joint.offset[0],
            joint.offset[1],
            joint.offset[2]),
            OpenMaya.MSpace.kTransform)
        joints.append(bone)
        mjoints.append(mbone)
        weightIndices.append(i)
    # Create Maya Arrays
    weightVals = OpenMaya.MDoubleArray(len(pskfile.wedges) * weightIndices.length())
    vertexArray = OpenMaya.MFloatPointArray()
    polygonCounts = OpenMaya.MIntArray(len(pskfile.faces), 3)
    polygonConnects = OpenMaya.MIntArray()
    uArray = OpenMaya.MFloatArray()
    vArray = OpenMaya.MFloatArray()
    # Material Faces
    materialPolys = {}
    materials = {}
    # Materials
    # Add Materials
    for i, material in enumerate(pskfile.materials):
        shader = cmds.shadingNode("lambert", name=material.name, asShader=True)
        materials[i] = shader
        materialPolys[i] = []
    # Add Vertex Data
    weight = 0
    for i, wedge in enumerate(pskfile.wedges):
        vertexArray.append(
            pskfile.vertices[wedge.point].offset[0],
            pskfile.vertices[wedge.point].offset[1], 
            pskfile.vertices[wedge.point].offset[2])
        uArray.append(wedge.uv[0])
        vArray.append(1 - wedge.uv[1])
        weights = pskfile.weights[wedge.point]
        for j in range(weightIndices.length()):
            weightVals[weight] = weights[j]
            weight += 1
    # Add Face Data
    fid = 0
    for i, face in enumerate(pskfile.faces):
        polygonConnects.append(face.wedges[0])
        polygonConnects.append(face.wedges[2])
        polygonConnects.append(face.wedges[1])
        materialPolys[face.material_index].append(i)
    # Create Maya Mesh
    mesh = OpenMaya.MFnMesh()
    transform = mesh.create(
        vertexArray.length(),
        len(pskfile.faces),
        vertexArray,
        polygonCounts,
        polygonConnects)
    # Assign UVs
    mesh.setUVs(uArray, vArray)
    mesh.assignUVs(polygonCounts, polygonConnects)
    # Create Groups and assign Material/s
    mtransform = OpenMaya.MFnTransform().create()
    mtransform.setName("PSKMeshes")
    dagPath = OpenMaya.MDagPath()
    OpenMaya.MDagPath.getAPathTo(transform, dagPath)
    newPath = cmds.parent(dagPath.fullPathName(), "PSKMeshes")
    newPath = cmds.rename(newPath, "PSKMesh")
    cmds.select(newPath)
    # TODO: Improve on face Materials, currently in all
    # cases I've found material faces to run in a series
    # but I'm unsure if they can be spread out and might throw this off
    for index in materialPolys:
        cmds.select(newPath + ".f[%i:%i]" %
        (materialPolys[index][0], materialPolys[index][-1]), r=True)
        cmds.hyperShade(assign=materials[index])
    cmds.select(clear = True)
    for joint in mjoints:
        cmds.select(joint.partialPathName(), add = True)
    cmds.select(newPath, add = True)
    # Set Weights
    cluster = cmds.skinCluster(tsb = True)
    selList = OpenMaya.MSelectionList()
    selList.add(cluster[0])
    clusterNode = OpenMaya.MObject()
    selList.getDependNode(0, clusterNode)
    skin = OpenMayaAnim.MFnSkinCluster(clusterNode)
    cmds.select(clear = True)
    skin.setWeights(
        dagPath,
        mObj,
        weightIndices,
        weightVals)

CreateMenu()