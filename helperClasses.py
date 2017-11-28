import sys
import pygame
import numpy as np

from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo

class Vertex:
    def __init__(self, pos, color):
        self.position = [pos]
        self.color = [color]
        
    def set_pos(self, pos): 
        self.position = pos
        
    def get_pos(self):
        return self.position

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color

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

class Shape:
    all_shapes = []
    
    def __init__(self):
        self.pos = [0,0,0]
        self.triangles = []
        self.all_shapes.append(self)
        
    def become_rect(self, length, height, color):
        v1 = Vertex([0, 0],color)
        v2 = Vertex([length, 0],color)
        v3 = Vertex([length, height],color)
        v4 = Vertex([0, height],color)
        
        t1 = Triangle([v1,v2,v3])
        t2 = Triangle([v1,v3,v4])
                
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
    
    def num_tris(self):
        return len(self.triangles)