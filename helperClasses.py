import sys
import pygame
import numpy as np

from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo

class Vertex:
    def __init__(self, pos, norm, color):
        self.position = pos
        self.normal = norm
        self.color = color

    def set_pos(self, pos):
        self.position = pos

    def get_pos(self):
        return self.position

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def set_norm(self, norm):
        self.normal = norm

    def get_norm(self):
        return self.normal

class Triangle:
    def __init__(self, vert_positions):
        self.v1 = vert_positions[0]
        self.v2 = vert_positions[1]
        self.v3 = vert_positions[2]

    def get_verts(self):
        return [self.v1,self.v2,self.v3]

    def get_verts_pos(self):
        return self.v1.get_pos() + self.v2.get_pos() + self.v3.get_pos()

    def get_verts_color(self):
        return self.v1.get_color() + self.v2.get_color() + self.v3.get_color()

    def get_verts_normal(self):
        return self.v1.get_norm() + self.v2.get_norm() + self.v3.get_norm()

class Shape:
    all_shapes = []

    def __init__(self):
        self.pos = [0,0,0]
        self.triangles = []
        self.all_shapes.append(self)

    def become_rect(self, length, height, color):
        ul_pos = [0, 0]
        ur_pos = [0, -height]
        ll_pos = [length, 0]
        lr_pos = [length, -height]
        c_pos = [length/2.0, -height/2.0]

        up_norm = [0,1]
        down_norm = [0,-1]
        right_norm = [1,0]
        left_norm = [-1,0]

        v1 = Vertex(ul_pos, up_norm, color)
        v2 = Vertex(ur_pos, up_norm, color)
        v3 = Vertex(c_pos, [0,0], color)
        t1 = Triangle([v1,v2,v3])

        v4 = Vertex(ur_pos, right_norm, color)
        v5 = Vertex(lr_pos, right_norm, color)
        v6 = Vertex(c_pos, [0,0], color)
        t2 = Triangle([v4,v5,v6])

        v7 = Vertex(lr_pos, down_norm, color)
        v8 = Vertex(ll_pos, down_norm, color)
        v9 = Vertex(c_pos, [0,0], color)
        t3 = Triangle([v7,v8,v9])

        v10 = Vertex(ul_pos, left_norm, color)
        v11 = Vertex(ll_pos, left_norm, color)
        v12 = Vertex(c_pos, [0,0], color)
        t4 = Triangle([v10,v11,v12])


        self.triangles = [t1,t2,t3,t4]

    def pos_vbo(self):
        data = []
        for tri in self.triangles:
            data.append(tri.get_verts_pos())
        return vbo.VBO(np.array(data,'f'))

    def color_vbo(self):
        data = []
        for tri in self.triangles:
            data.append(tri.get_verts_color())
        return vbo.VBO(np.array(data,'f'))

    def normal_vbo(self):
        data = []
        for tri in self.triangles:
            data.append(tri.get_verts_normal())
        return vbo.VBO(np.array(data,'f'))

    def num_tris(self):
        return len(self.triangles)
