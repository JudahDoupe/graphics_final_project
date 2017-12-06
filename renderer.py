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
        glUniform2fv(translation_loc, 1, shape.get_position())
        glDrawArrays(GL_TRIANGLES, 0, shape.num_tris() * 3)

    pygame.display.flip()
    pygame.time.wait(10)


def setup_dir_lights(program, dir_lights):
    light_index = 0

    directionLocation = glGetUniformLocation(program, "u_directionalLightD")
    intensityLocation = glGetUniformLocation(program, "u_directionalLightIntensity")

    directions = []
    intensities = []

    for light in dir_lights:
        directions = directions + light.get_direction()
        intensities = intensities + [light.get_intensity()]
        light_index += 1
        if light_index > 3 :
            return

    while  light_index < 3:
        directions = directions + [0,0]
        intensities = intensities + [0]
        light_index += 1

    print(intensities)
    glUniform2fv(directionLocation, 3, np.array(directions,'f'))
    glUniform1fv(intensityLocation, 3, np.array(intensities,'f'))


def setup_point_lights(program, point_light):
    light_index = 0

    positionLocation = glGetUniformLocation(program, "u_pointLightP")
    intensityLocation = glGetUniformLocation(program, "u_pointLightIntensity")

    positions = []
    intensities = []

    for light in point_light:
        positions = positions + light.get_position()
        intensities = intensities + [light.get_intensity()]
        light_index += 1
        if light_index > 16 :
            return

    while  light_index < 16 :
        positions = positions + [0,0]
        intensities = intensities + [0]
        light_index += 1

    glUniform2fv(positionLocation, 16, np.array(positions,'f'))
    glUniform1fv(intensityLocation, 16, np.array(intensities,'f'));
