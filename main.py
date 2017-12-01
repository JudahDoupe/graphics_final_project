import sys
import pygame
import numpy as np

from math import sin, cos
from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo
from helperClasses import *

red = [1, 0.2, 0.3, 0]
green = [0.2, 1, 0.3, 0]
blue = [0.3, 0.5, 1, 0]

vertex_code = """
attribute vec2 a_position;
attribute vec4 a_color;
attribute vec2 a_normal;

uniform vec2 u_translation;

varying vec4 v_color;
varying vec2 v_normal;

void main()
{
    gl_Position = vec4(a_position + u_translation, 0, 1);
    v_color = a_color;
    v_normal = a_normal;
}


"""

fragment_code = """
uniform vec2 u_reverseLightDirection;
precision mediump float;
varying vec4 v_color;
varying vec2 v_normal;

void main()
{
    vec2 normal = normalize(v_normal);

    float light = max(dot(v_normal, u_reverseLightDirection),.1);
    gl_FragColor = v_color * light;
}
"""


def draw(dir_light_dir):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glUseProgram(program)

    reverseLightDirectionLocation = glGetUniformLocation(program, "u_reverseLightDirection")
    glUniform2f(reverseLightDirectionLocation, sin(dir_light_dir), cos(dir_light_dir))

    for shape in Shape.all_shapes:
        position_buffer = shape.pos_vbo()
        position_buffer.bind()
        position_loc = glGetAttribLocation(program, 'a_position')
        glEnableVertexAttribArray(position_loc)
        glVertexAttribPointer(position_loc, 2, GL_FLOAT, False, 0, position_buffer )

        color_buffer = shape.color_vbo()
        color_buffer.bind()
        color_loc = glGetAttribLocation(program, 'a_color')
        glEnableVertexAttribArray(color_loc)
        glVertexAttribPointer(color_loc, 4, GL_FLOAT, False, 0, color_buffer )

        normal_buffer = shape.normal_vbo()
        normal_buffer.bind()
        normal_loc = glGetAttribLocation(program, 'a_normal')
        glEnableVertexAttribArray(normal_loc)
        glVertexAttribPointer(normal_loc, 2, GL_FLOAT, False, 0, normal_buffer )

        normal_loc = glGetUniformLocation(program, 'u_translation')
        glUniform2f(normal_loc, shape.get_transform()[0], shape.get_transform()[1],)

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


def generate_elements():
    dir_light = "dir_light"
    element_list = [dir_light]  #Add any elements, lights, shapes etc. into this array
    
    square1 = Shape()
    square1.become_rect(1,1,red)
    square1.set_transform([-0.5,-0.5])
    element_list.append(square1)

    square2 = Shape()
    square2.become_rect(0.5,0.5,green)
    square2.set_transform([-0.2,0])
    element_list.append(square2)
        
    square3 = Shape()
    square3.become_rect(0.75,0.75,blue)
    square3.set_transform([0.3,0.25])
    element_list.append(square3)
    
    return element_list
    
    
def draw_gui():
    return
    
    
def main():
    setup()
    
    element_list = generate_elements()
    
    #pygame stuff
    dir_var = 0
    selected_element_id = 0
    selected_element = element_list[selected_element_id]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    quit()
                elif event.key == K_TAB:
                    if selected_element_id == len(element_list):
                        selected_element_id = 0
                    else:
                        selected_element_id += 1
                    selected_element = element_list[selected_element_id]
        key = pygame.key.get_pressed()
        if selected_element == "dir_light":
            if key[K_RIGHT]:
                dir_var -=0.2
                dir_var = dir_var % 6.2
            elif key[K_LEFT]:
                dir_var += 0.2
                dir_var = dir_var % 6.2
        else:
            if key[K_RIGHT]:
                selected_element.set_transform(selected_element.get_transform()[0] + 1, selected_element.get_transform()[1])
            elif key[K_LEFT]:
                selected_element.set_transform(selected_element.get_transform()[0] - 1, selected_element.get_transform()[1])
            elif key[K_UP]:
                selected_element.set_transform(selected_element.get_transform()[0], selected_element.get_transform()[1] + 1)
            elif key[K_DOWN]:
                selected_element.set_transform(selected_element.get_transform()[0], selected_element.get_transform()[1] - 1)
        draw(dir_var)
        

main()