import sys
import pygame
import numpy as np

from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo

class Vertex:
    def __init__(self):
        self.position = [0,0,0]
        self.color = [0,0,0,0]

    def vert_to_array(self):  #Turns the vertex's x, y, z into one list to get parsed later for the buffer
        return self.position + self.color
        
    def set_pos(self, x, y, z):
        self.position = [x, y, z]
        
    def get_pos(self):
        return self.position

    def set_color(self, r, g, b, a):
        self.color = [r, g, b, a]

    def get_color(self):
        return self.color

class Triangle:
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.position = [0,0,0]
        
    def tri_to_array(self):  #Turns the triangle's x, y, z into one list to get parsed later for the buffer
        return self.v1.vert_to_array() + self.v2.vert_to_array() + self.v3.vert_to_array()

    def set_tri_pos(self, x, y, z):
        self.position = [x, y, z]
    
    def get_tri_pos(self):
        return self.position