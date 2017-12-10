import sys
import pygame
import numpy as np

from math import sin, cos
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from pygame.locals import *
from OpenGL.arrays import vbo
from helperClasses import *

class DeferredRenderer:

    geomenty_vertex_code = """
        uniform vec2 u_resolution;

        attribute vec2 a_positionP;
        attribute vec2 a_normalV;
        attribute vec4 a_color;

        uniform vec2 u_translationV;

        varying vec2 v_positionP;
        varying vec2 v_normalV;
        varying vec4 v_color;

        void main() {
            vec2 positionP = a_positionP + u_translationV;
            vec2 clipSpaceP = (((positionP/ u_resolution) * 2 ) - 1 ) * vec2(1, -1);

            v_positionP = clipSpaceP;
            v_normalV = a_normalV;
            v_color = a_color;

            gl_Position = vec4(clipSpaceP , 0, 1);
        }
    """
    geomenty_fragment_code = """
        precision highp float;

        varying vec2 v_positionP;
        varying vec2 v_normalV;
        varying vec4 v_color;

        layout (location = 0) out vec2 FragPosition;
        layout (location = 1) out vec2 FragNormal;
        layout (location = 2) out vec4 FragColor;

        void main() {
            FragPosition = v_positionP;
            FragNormal = v_normalV;
            FragColor = v_color;
        }
    """
    lighting_vertex_code = """

    """
    lighting_fragment_code = """

    """

    def __init__(self):
        pygame.init()
        infoObject = pygame.display.Info()
        self.width  = infoObject.current_w
        self.height = infoObject.current_h
        self.surface = pygame.display.set_mode((self.width, self.height), DOUBLEBUF|OPENGL)

        self.geomenty_program  = self.create_program(self.geomenty_vertex_code, self.geomenty_fragment_code)
        #self.lighting_program  = self.create_program(self.lighting_vertex_code, self.lighting_fragment_code)

        self.geometry_buffer = glGenFramebuffers(1)

        self.positionTexture = self.gen_frame_buf_texture(self.geometry_buffer, 0)
        self.normalTexture = self.gen_frame_buf_texture(self.geometry_buffer, 1)
        self.colorTexture = self.gen_frame_buf_texture(self.geometry_buffer, 2)

        glBindFramebuffer(GL_FRAMEBUFFER, self.geometry_buffer)
        glDrawBuffers(3, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2])

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("Failed To Create G-Buffer");



    def draw(self):
        self.fill_geometry_buffer()

        for light in DirectionalLight.all_dir_lights:
            pass

        for light in PointLight.all_point_lights:
            pass

        pygame.display.flip()
        pygame.time.wait(10)



    def fill_geometry_buffer(self):
        glUseProgram(self.geomenty_program)
        glBindFramebuffer(GL_FRAMEBUFFER, self.geometry_buffer);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_TEXTURE_2D);

        glUniform2f(glGetUniformLocation(self.geomenty_program, "u_resolution"), self.width, self.height)

        for shape in Shape.all_shapes:
            self.fill_attribute(self.geomenty_program, shape.pos_vbo(), 'a_positionP', 2)
            self.fill_attribute(self.geomenty_program, shape.color_vbo(), 'a_color', 4)
            self.fill_attribute(self.geomenty_program, shape.normal_vbo(), 'a_normalV', 2)
            glUniform2fv(glGetUniformLocation(self.geomenty_program, 'u_translationV'), 1, shape.get_position())

            glDrawArrays(GL_TRIANGLES, 0, shape.num_tris() * 3)

        glBindFramebuffer(GL_FRAMEBUFFER, 0);



    def gen_frame_buf_texture(self, frame_buffer, index):
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)

        glBindFramebuffer(GL_FRAMEBUFFER, frame_buffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + index, GL_TEXTURE_2D, texture, 0)

        return texture

    def fill_attribute(self, program, vbo, name, size):
        vbo.bind()
        loc = glGetAttribLocation(program, name)
        glEnableVertexAttribArray(loc)
        glVertexAttribPointer(loc, size, GL_FLOAT, False, 0, vbo )

    def create_program(self, vert_shader, frag_shader):
        program  = glCreateProgram()
        vertex   = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)

        glShaderSource(vertex, vert_shader)
        glShaderSource(fragment, frag_shader)

        glCompileShader(vertex)
        glCompileShader(fragment)

        glAttachShader(program, vertex)
        glAttachShader(program, fragment)

        glLinkProgram(program)

        return program



