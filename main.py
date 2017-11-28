import sys
import pygame
import numpy as np

from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo
from helperClasses import *

red = [1, 0.2, 0.3, 0]
green = [0.2, 1, 0.3, 0]
blue = [0.4, 0.1, 1, 0.5]

vertex_code = """
attribute vec2 a_position;
attribute vec4 a_color;

varying vec4 v_color;

void main()
{
    gl_Position = vec4(a_position, 0, 1);
    v_color = a_color;
}
"""

fragment_code = """
precision mediump float;
varying vec4 v_color;

void main()
{
    gl_FragColor = v_color;
}
"""


def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glUseProgram(program)


    for shape in Shape.all_shapes:
        position_buffer = shape.pos_vbo()
        position_buffer.bind()
        position_loc = glGetAttribLocation(program, 'a_position')
        glEnableVertexAttribArray(position_loc);
        glVertexAttribPointer(position_loc, 2, GL_FLOAT, False, 0, position_buffer )

        color_buffer = shape.color_vbo()
        color_buffer.bind()
        color_loc = glGetAttribLocation(program, 'a_color')
        glEnableVertexAttribArray(color_loc);
        glVertexAttribPointer(color_loc, 4, GL_FLOAT, False, 0, color_buffer )

        glDrawArrays(GL_TRIANGLES, 0, shape.num_tris() * 3)

    pygame.display.flip()
    pygame.time.wait(10)


def setup():
    global program

    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

     # Request a program and shader slots from GPU
    program  = glCreateProgram()
    vertex   = glCreateShader(GL_VERTEX_SHADER)
    fragment = glCreateShader(GL_FRAGMENT_SHADER)

    # Set shaders source
    glShaderSource(vertex, vertex_code)
    glShaderSource(fragment, fragment_code)

    # Compile shaders
    glCompileShader(vertex)
    glCompileShader(fragment)

    # Attach shader objects to the program
    glAttachShader(program, vertex)
    glAttachShader(program, fragment)

    # Build program
    glLinkProgram(program)


def main():
    setup()

    square = Shape()
    square.become_rect(1,1,blue)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        draw()

main()
