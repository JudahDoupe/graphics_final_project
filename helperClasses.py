import sys
import pygame
import numpy as np

from math import sin, cos, atan2
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

class Element:
    all_elements = []


class Shape(Element):
    all_shapes = []

    def __init__(self, length, height, color):
        ul_vert = Vertex([0, 0], [-0.5 , -0.5] , color)
        ur_vert = Vertex([length, 0], [0.5, -0.5], color)
        ll_vert = Vertex([0, height], [-0.5, 0.5], color)
        lr_vert = Vertex([length, height], [0.5, 0.5], color)

        t1 = Triangle([ul_vert,ur_vert,lr_vert])
        t2 = Triangle([lr_vert,ll_vert,ul_vert])

        self.triangles = [t1,t2]
        self.position = [0,0]
        self.all_shapes.append(self)
        self.all_elements.append(self)
        self.element_type = "shape"

    def is_light(self):
        return False

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

    def get_position(self):
        return self.position;

    def set_position(self, position):
        self.position = position


class DirectionalLight(Element):
    all_dir_lights = []

    def __init__(self, direction, color, intensity):
        self.direction = direction
        self.all_dir_lights.append(self)
        self.all_elements.append(self)
        self.element_type = "dir_light"
        self.color = color
        self.intensity = intensity

    def is_light(self):
        return True

    def get_direction(self):
        return self.direction;

    def get_direction_in_radians(self):
        return atan2(self.direction[1], self.direction[0])

    def set_direction(self, angle_in_radians):
        self.direction = [cos(angle_in_radians), sin(angle_in_radians)]

    def get_intensity(self):
        return self.intensity;

    def set_intensity(self, intensity):
        self.intensity = intensity

    def get_color(self):
        return self.color;

    def set_color(self, color):
        self.color = color


class PointLight(Element):
    all_point_lights = []

    def __init__(self, position, color, intensity):
        self.position = position
        self.all_point_lights.append(self)
        self.all_elements.append(self)
        self.element_type = "point_light"
        self.color = color
        self.intensity = intensity

    def is_light(self):
        return True

    def get_position(self):
        return self.position;

    def set_position(self, position):
        self.position = position

    def get_intensity(self):
        return self.intensity;

    def set_intensity(self, intensity):
        self.intensity = intensity

    def get_color(self):
        return self.color;

    def set_color(self, color):
        self.color = color


class SpotLight(Element):
    all_spot_lights = []

    def __init__(self, position, direction, color, intensity):
        self.position = position
        self.direction = direction
        self.all_spot_lights.append(self)
        self.all_elements.append(self)
        self.element_type = "point_light"
        self.color = color
        self.intensity = intensity

    def is_light(self):
        return True

    def get_position(self):
        return self.position;

    def set_position(self, position):
        self.position = position

    def get_direction(self):
        return self.direction;

    def get_direction_in_radians(self):
        return atan2(self.direction[1], self.direction[0])

    def set_direction(self, angle_in_radians):
        self.direction = [cos(angle_in_radians), sin(angle_in_radians)]

    def get_intensity(self):
        return self.intensity;

    def set_intensity(self, intensity):
        self.intensity = intensity

    def get_color(self):
        return self.color;

    def set_color(self, color):
        self.color = color
