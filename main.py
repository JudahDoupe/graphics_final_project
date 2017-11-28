import sys
import pygame
import numpy as np

from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo
from helperClasses import *

red = [1, 0.2, 0.3, 0]
green = [0.2, 1, 0.3, 0]
blue = [0.4, 0.1, 1, 0]

vertex_code = """
attribute vec2 a_position;
uniform mat3 u_matrix;

void main()
{
    vec2 xy = (u_matrix * vec3(a_position, 1)).xy;
    gl_Position = vec4(xy, 0, 1);
}
"""

fragment_code = """
precision mediump float;

uniform vec4 u_color;

void main()
{
    gl_FragColor = u_color;
}
"""


vertexBuffer = vbo.VBO(np.array( [
            [ 0, 1, 0],
            [-1,-1, 0],
            [ 1,-1, 1],
        ],'f'))


def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glUseProgram(program)

    for shape in Shape.all_shapes:
        print("butts")
        buffer = shape.shape_to_vbo()
        buffer.bind()
        glEnableClientState(GL_VERTEX_ARRAY);
        glVertexPointer(3, GL_FLOAT, 4, vertexBuffer ) # glVertexPointer( size , type , stride , pointer )
    glDrawArrays(GL_TRIANGLES, 0, 9) # glDrawArrays( mode , first, count )

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

    # Get rid of shaders (no more needed)
    glDetachShader(program, vertex)
    glDetachShader(program, fragment)


def main():
    setup()

    square = Shape()
    square.become_rect(5,5,blue)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        draw()

main()
