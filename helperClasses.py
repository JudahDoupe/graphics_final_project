import sys
import pygame

from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo

class Vertex:
    def __init__(self, pos, color):
        self.position = [pos]
        self.color = [color]

    def vert_to_array(self):  #Turns the vertex's x, y into one list to get parsed later for the buffer
        return self.position + self.color
        
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
        
    def tri_to_array(self):  #Turns the triangle's x, y, z into one list to get parsed later for the buffer
        return self.v1.vert_to_array() + self.v2.vert_to_array() + self.v3.vert_to_array()
        
    def get_tri_verts(self):
        return [self.v1, self.v2, self.v3]

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
        
    def shape_to_vbo(self):
        data = []
        for tri in self.triangles:
            data.append(tri.tri_to_array())
        return vbo.VBO(data,'f')
    
    def num_tris(self):
        return len(triangles)