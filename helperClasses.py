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
        self.pos = [0,0]
        self.triangles = []
        self.all_shapes.append(self)

    def become_rect(self, length, height, color):
        ul_pos = [0, 0]
        ur_pos = [length, 0]
        ll_pos = [0, height]
        lr_pos = [length, height]


        v1 = Vertex(ul_pos, [-0.5 , 0.5] , color)     #right
        v2 = Vertex(ur_pos, [0.5, 0.5], color)
        v3 = Vertex(ll_pos, [-0.5, -0.5], color)
        t1 = Triangle([v1,v2,v3])

        v4 = Vertex(ur_pos, [0.5, 0.5], color)    #up
        v5 = Vertex(lr_pos, [0.5, -0.5], color)
        v6 = Vertex(ll_pos, [-0.5, -0.5], color)
        t2 = Triangle([v4,v5,v6])


        self.triangles = [t1,t2]

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

    def get_transform(self):
        return self.pos;

    def set_transform(self, transform):
        self.pos = transform

    def num_tris(self):
        return len(self.triangles)
