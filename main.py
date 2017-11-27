import sys
import pygame
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from pygame.locals import *

from OpenGL.arrays import vbo

vertex_code = """
void main() {
    gl_Position = ftransform();
    gl_FrontColor = abs(gl_Position);
}
"""

fragment_code = """
void main() {
    gl_FragColor = gl_Color;
}"""


vertexBuffer = vbo.VBO(np.array( [
            [ 0, 1, 0],
            [-1,-1, 0],
            [ 1,-1, 1],
        ],'f'))


def draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glUseProgram(program)

    try:
        vertexBuffer.bind()
        try:
            glEnableClientState(GL_VERTEX_ARRAY);
            # glVertexPointer( size , type , stride , pointer )
            glVertexPointer(3, GL_FLOAT, 12, vertexBuffer )
            # glDrawArrays( mode , first, count )
            glDrawArrays(GL_TRIANGLES, 0, 9)
        finally:
            vertexBuffer.unbind()
            glDisableClientState(GL_VERTEX_ARRAY);
    finally:
        glUseProgram( 0 )

    pygame.display.flip()
    pygame.time.wait(10)


def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    global program

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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        draw()

main()