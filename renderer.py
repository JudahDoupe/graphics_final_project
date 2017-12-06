import sys
import pygame
import numpy as np

from math import sin, cos
from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo
from helperClasses import *



def draw(program, shapes, dir_lights, point_lights):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glUseProgram(program)

    resolutionLocation = glGetUniformLocation(program, "u_resolution")
    w, h = pygame.display.get_surface().get_size()
    glUniform2f(resolutionLocation, w, h)

    setup_dir_lights(program, dir_lights)

    setup_point_lights(program, point_lights)


    for shape in shapes:
        position_buffer = shape.pos_vbo()
        position_buffer.bind()
        position_loc = glGetAttribLocation(program, 'a_positionP')
        glEnableVertexAttribArray(position_loc)
        glVertexAttribPointer(position_loc, 2, GL_FLOAT, False, 0, position_buffer )

        color_buffer = shape.color_vbo()
        color_buffer.bind()
        color_loc = glGetAttribLocation(program, 'a_color')
        glEnableVertexAttribArray(color_loc)
        glVertexAttribPointer(color_loc, 4, GL_FLOAT, False, 0, color_buffer )

        normal_buffer = shape.normal_vbo()
        normal_buffer.bind()
        normal_loc = glGetAttribLocation(program, 'a_normalV')
        glEnableVertexAttribArray(normal_loc)
        glVertexAttribPointer(normal_loc, 2, GL_FLOAT, False, 0, normal_buffer )

        translation_loc = glGetUniformLocation(program, 'u_translationV')
        glUniform2f(translation_loc, shape.get_position()[0], shape.get_position()[1])
        glDrawArrays(GL_TRIANGLES, 0, shape.num_tris() * 3)

    pygame.display.flip()
    pygame.time.wait(10)


def setup_shape(program, shape):
    position_buffer = shape.pos_vbo()
    position_buffer.bind()
    position_loc = glGetAttribLocation(program, 'a_positionP')
    glEnableVertexAttribArray(position_loc)
    glVertexAttribPointer(position_loc, 2, GL_FLOAT, False, 0, position_buffer )

    color_buffer = shape.color_vbo()
    color_buffer.bind()
    color_loc = glGetAttribLocation(program, 'a_color')
    glEnableVertexAttribArray(color_loc)
    glVertexAttribPointer(color_loc, 4, GL_FLOAT, False, 0, color_buffer )

    normal_buffer = shape.normal_vbo()
    normal_buffer.bind()
    normal_loc = glGetAttribLocation(program, 'a_normalV')
    glEnableVertexAttribArray(normal_loc)
    glVertexAttribPointer(normal_loc, 2, GL_FLOAT, False, 0, normal_buffer )

    normal_loc = glGetUniformLocation(program, 'u_translationV')
    glUniform2f(normal_loc, shape.get_position()[0], shape.get_position()[1])

def setup_dir_lights(program, dir_lights):
    light_index = 0

    directionLocation = glGetUniformLocation(program, "u_directionalLightD")
    intensityLocation = glGetUniformLocation(program, "u_directionalLightIntensity")

    for light in dir_lights:
        glUniform2f(directionLocation, light.get_direction()[0], light.get_direction()[1])
        glUniform1f(intensityLocation, light.get_intensity());
        light_index += 1
        if light_index > 1 :
            return

    while  light_index < 1:
        glUniform2f(directionLocation, 0, 1)
        glUniform1f(intensityLocation, 0);
        light_index += 1


def setup_point_lights(program, point_light):
    light_index = 0

    positionLocation = glGetUniformLocation(program, "u_pointLightP")
    intensityLocation = glGetUniformLocation(program, "u_pointLightIntensity")

    for light in point_light:
        glUniform2f(positionLocation, light.get_position()[0], light.get_position()[1])
        glUniform1f(intensityLocation, light.get_intensity());
        light_index += 1
        if light_index > 1 :
            return

    while  light_index < 1 :
        glUniform2f(positionLocation, 0, 0)
        glUniform1f(intensityLocation, 0);
        light_index += 1
