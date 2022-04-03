"""
    PSK Python Library for loading PSK Mesh/Skeletal Data - Version 0.1.0
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
import struct

class Utils:
    @staticmethod
    def ReadFixedString(f, size):
        """ Reads and Trims a fixed size string """
        return f.read(size).rstrip(b'\0').decode("utf-8")

    @staticmethod
    def ReadChar(f):
        """ Reads a signed 8 bit int """
        return struct.unpack("b", f.read(1))[0]

    @staticmethod
    def ReadUnsignedChar(f):
        """ Reads an unsigned 8 bit int """
        return struct.unpack("B", f.read(1))[0]

    @staticmethod
    def ReadShort(f):
        """ Reads a signed 16 bit int """
        return struct.unpack("h", f.read(2))[0]

    @staticmethod
    def ReadUnsignedShort(f):
        """ Reads an unsigned 16 bit int """
        return struct.unpack("H", f.read(2))[0]

    @staticmethod
    def ReadInt(f):
        """ Reads a signed 32 bit int """
        return struct.unpack("i", f.read(4))[0]

    @staticmethod
    def ReadUnsignedInt(f):
        """ Reads an unsigned 32 bit int """
        return struct.unpack("I", f.read(4))[0]

    @staticmethod
    def ReadFloat(f):
        """ Reads a float """
        return struct.unpack("f", f.read(4))[0]

    @staticmethod
    def ReadVector2(f):
        """ Reads a vector of size 2 """
        return struct.unpack("ff", f.read(8))

    @staticmethod
    def ReadVector3(f):
        """ Reads a vector of size 3 """
        return struct.unpack("fff", f.read(12))

    @staticmethod
    def ReadVector4(f):
        """ Reads a vector of size 4 """
        return struct.unpack("ffff", f.read(16))


class Vertex:
    """ Class to hold PSK Vertex Data """
    def __init__(self, offset = []):
        self.offset             = offset

class Wedge:
    """ Class to hold PSK Wedge Data """
    def __init__(self, point, uv, material_index):
        self.point              = point
        self.uv                 = uv
        self.material_index     = material_index

class Face:
    """ Class to hold PSK Face Data """
    def __init__(self, wedges, material_index, aux_mat_index, smoothing_group):
        self.wedges = wedges
        self.material_index     = material_index
        self.aux_mat_index      = aux_mat_index
        self.smoothing_group    = smoothing_group

class Bone:
    """ Class to hold PSK Bone Data """
    def __init__(self, name, parent, offset, rotation, scale):
        self.name               = name
        self.parent             = parent
        self.offset             = offset
        self.rotation           = rotation
        self.scale              = scale

class Material:
    """ Class to hold PSK Material Data """
    def __init__(self, name):
        self.name               = name

class Weight:
    """ Class to hold PSK Vertex Weight Data """
    def __init__(self, vertex_index, bone_index, influence):
        self.vertex_index       = vertex_index
        self.bone_index         = bone_index
        self.influence          = influence

class UnrealPSK:
    """ Class to hold PSK Data """
    def LoadActorHeadChunk(self, psk_file, data_size, data_count):
        """ Loads Header from a PSK File """
        pass

    def LoadVertexChunk(self, psk_file, data_size, data_count):
        """ Loads Vertex Data from a PSK File """
        self.vertices = [None] * data_count
        for i in range(data_count):
            self.vertices[i] = Vertex(Utils.ReadVector3(psk_file))

    def LoadFaceChunk(self, psk_file, data_size, data_count):
        """ Loads Face Data from a PSK File """
        self.faces = [None] * data_count
        for i in range(data_count):
            wedge1          = Utils.ReadUnsignedShort(psk_file)
            wedge2          = Utils.ReadUnsignedShort(psk_file)
            wedge3          = Utils.ReadUnsignedShort(psk_file)
            mat_index       = Utils.ReadUnsignedChar(psk_file)
            aux_mat_index   = Utils.ReadUnsignedChar(psk_file)
            smooth_group    = Utils.ReadUnsignedInt(psk_file)
            self.faces[i]   = Face(
                [wedge1, wedge2, wedge3],
                mat_index,
                aux_mat_index,
                smooth_group)
    
    def LoadFaceChunk32(self, psk_file, data_size, data_count):
        """ Loads 32bit Face Data from a PSK File """
        self.faces = [None] * data_count
        for i in range(data_count):
            wedge1          = Utils.ReadUnsignedInt(psk_file)
            wedge2          = Utils.ReadUnsignedInt(psk_file)
            wedge3          = Utils.ReadUnsignedInt(psk_file)
            mat_index       = Utils.ReadUnsignedChar(psk_file)
            aux_mat_index   = Utils.ReadUnsignedChar(psk_file)
            smooth_group    = Utils.ReadUnsignedInt(psk_file)
            self.faces[i]   = Face(
                [wedge1, wedge2, wedge3],
                mat_index,
                aux_mat_index,
                smooth_group)

    def LoadWedgeChunk(self, psk_file, data_size, data_count):
        """ Loads Wedge Data from a PSK File """
        self.wedges = [None] * data_count
        for i in range(data_count):
            point           = Utils.ReadUnsignedInt(psk_file)
            uv              = Utils.ReadVector2(psk_file)
            material        = Utils.ReadUnsignedInt(psk_file)
            self.wedges[i]  = Wedge(point, uv, material)

    def LoadSkeletonChunk(self, psk_file, data_size, data_count):
        """ Loads Skeleton Data from a PSK File """
        self.bones = [None] * data_count
        for i in range(data_count):
            name            = Utils.ReadFixedString(psk_file, 64)
            flags           = Utils.ReadUnsignedInt(psk_file)
            child_count     = Utils.ReadUnsignedInt(psk_file)
            parent          = Utils.ReadUnsignedInt(psk_file)
            rotation        = Utils.ReadVector4(psk_file)
            offset          = Utils.ReadVector3(psk_file)
            length          = Utils.ReadFloat(psk_file)
            scale           = Utils.ReadVector3(psk_file)
            self.bones[i]   = Bone(
                name,
                parent,
                offset,
                rotation,
                scale)

    def LoadMaterialChunk(self, psk_file, data_size, data_count):
        """ Loads Material Data from a PSK File """
        self.materials = [None] * data_count
        for i in range(data_count):
            name                = Utils.ReadFixedString(psk_file, 64)
            texture_index       = Utils.ReadUnsignedInt(psk_file)
            poly_flags          = Utils.ReadUnsignedInt(psk_file)
            aux_mat             = Utils.ReadUnsignedInt(psk_file)
            aux_flags           = Utils.ReadUnsignedInt(psk_file)
            lod_bias            = Utils.ReadUnsignedInt(psk_file)
            lod_style           = Utils.ReadUnsignedInt(psk_file)
            self.materials[i]   = Material(name)

    def LoadWeightChunk(self, psk_file, data_size, data_count):
        """ Loads Weight Data from a PSK File """
        for i in range(data_count):
            influence           = Utils.ReadFloat(psk_file)
            vertex_index        = Utils.ReadUnsignedInt(psk_file)
            bone_index          = Utils.ReadUnsignedInt(psk_file)
            if vertex_index not in self.weights:
                self.weights[vertex_index] = [0.0] * len(self.bones)
            self.weights[vertex_index][bone_index] = influence

    def LoadExtraUVChunk(self, psk_file, data_size, data_count):
        """ Loads Extra UV Data from a PSK File """
        u = Utils.ReadFloat(psk_file)
        v = Utils.ReadFloat(psk_file)

    def __init__(self, psk_file = None):
        """ Initiates PSK File """
        self.vertices = []
        self.wedges = []
        self.faces = []
        self.materials = []
        self.bones = []
        self.weights = {}
        # Load PSK if passed
        if psk_file:
            self.load_psk_file(psk_file)


    def load_psk_file(self, psk_file):
        """ Loads a PSK File """
        # Known File Chunks
        chunk_map = {
            b'ACTRHEAD' : self.LoadActorHeadChunk,
            b'PNTS0000' : self.LoadVertexChunk,
            b'VTXW0000' : self.LoadWedgeChunk,
            b'VTXW3200' : self.LoadWedgeChunk,
            b'FACE0000' : self.LoadFaceChunk,
            b'FACE3200' : self.LoadFaceChunk32,
            b'REFSKELT' : self.LoadSkeletonChunk,
            b'REFSKEL0' : self.LoadSkeletonChunk,
            b'MATT0000' : self.LoadMaterialChunk,
            b'EXTRAUV0' : self.LoadExtraUVChunk,
            b'EXTRAUV1' : self.LoadExtraUVChunk,
            b'EXTRAUV2' : self.LoadExtraUVChunk,
            b'RAWWEIGHTS' : self.LoadWeightChunk
        }
        # Load PSK File
        with open(psk_file, 'rb') as f:
            # Read First Chunk
            chunk = f.read(20).rstrip(b'\0')
            while chunk:
                type_flag       = Utils.ReadUnsignedInt(f)
                data_size       = Utils.ReadUnsignedInt(f)
                data_count      = Utils.ReadUnsignedInt(f)
                # Load Chunk if we recognize it, otherwise skip
                if chunk in chunk_map:
                    chunk_map[chunk](f, data_size, data_count)
                else:
                    f.read(data_size * data_count)
                # Read Next Chunk
                chunk = f.read(20).rstrip(b'\0')
