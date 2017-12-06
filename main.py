import sys
import pygame
import numpy as np

from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo
from helperClasses import *
from renderer import *

red = [1, 0.2, 0.3, 0]
green = [0.2, 1, 0.3, 0]
blue = [0.3, 0.5, 1, 0]
white = [1, 1, 1, 0]

vertex_code = """
uniform vec2 u_resolution;

attribute vec4 a_color;
attribute vec2 a_positionP;
attribute vec2 a_normalV;
uniform vec2 u_translationV;

varying vec4 v_color;
varying vec2 v_positionP;
varying vec2 v_normalV;

uniform vec2 u_directionalLightD[3];
varying vec2 v_directionalLightReflectedD[3];

uniform vec2 u_pointLightP[16];
varying vec2 v_pointLightV[16];
varying vec2 v_pointLightReflectedD[16];

void main()
{
    vec2 positionP = a_positionP + u_translationV;
    vec2 clipSpaceP = (((positionP/ u_resolution) * 2 ) - 1 ) * vec2(1, -1);

    v_color = a_color;
    v_positionP = clipSpaceP;
    v_normalV = a_normalV;

    for (int i= 0; i < 3; i++){
        v_directionalLightReflectedD[i] = normalize(-1 * u_directionalLightD[i] + 2 * dot(a_normalV,u_directionalLightD[i])  * a_normalV);
    }

    for (int i= 0; i < 16; i++){
        v_pointLightV[i] = u_pointLightP[i] - positionP;
        v_pointLightReflectedD[i] = normalize(-1 * normalize(v_pointLightV[i]) + 2 * dot(a_normalV, normalize(v_pointLightV[i]))  * a_normalV);
    }

    gl_Position = vec4(clipSpaceP , 0, 1);
}


"""

fragment_code = """
precision mediump float;

varying vec4 v_color;
varying vec2 v_positionP;
varying vec2 v_normalV;

uniform vec2 u_directionalLightD[3];
uniform float u_directionalLightIntensity[3];
varying vec2 v_directionalLightReflectedD[3];

varying vec2 v_pointLightV[16];
uniform float u_pointLightIntensity[16];
varying vec2 v_pointLightReflectedD[16];

void main()
{
    vec4 ambientLightColor = v_color * 0.2;

    int specularExponent = 10;
    vec4 specularCoefficient = vec4(1, 1, 1, 0);

    gl_FragColor = ambientLightColor;

    for (int i= 0; i < 3; i++){
        vec4 directionalLightColor = vec4(0.7, 0.7, 0.7, 0);
        float directionalLightFraction = max(0,dot(v_normalV, u_directionalLightD[i]));
        vec4 directionalLightSpecular = specularCoefficient * pow( max( 0, dot( normalize(v_positionP), v_directionalLightReflectedD[i] )), specularExponent);

        gl_FragColor = gl_FragColor + directionalLightColor * (v_color + directionalLightSpecular) * directionalLightFraction * u_directionalLightIntensity[i];
    }
    
    for (int i= 0; i < 16; i++){
        vec4 pointLightColor = vec4(0.7, 0.7, 0.7, 0);
        float pointLightFraction = max(0,dot(v_normalV, normalize(v_pointLightV[i]))) / pow(length(v_pointLightV[i]),2) * 20000 * u_pointLightIntensity[i];
        vec4 pointLightSpecular = specularCoefficient * pow( max( 0, dot( normalize(v_positionP), v_pointLightReflectedD[i] )), specularExponent);

        gl_FragColor = gl_FragColor + pointLightColor * (v_color + pointLightSpecular) * pointLightFraction;
    }
}
"""

def setup():
    global program

    pygame.init()
    infoObject = pygame.display.Info()
    res = (infoObject.current_w, infoObject.current_h)
    surface = pygame.display.set_mode(res, DOUBLEBUF|OPENGL)

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

    return surface, res


def generate_elements():
    #dir_light = DirectionalLight([0.5,0.5],white, 1)
    point_light1 = PointLight([250,250],white,1)
    point_light2 = PointLight([750,250],white,1)

    for x in range(0, 1000, 100):
        floor = Shape(100,100,green)
        floor.set_position([x,500])

        ceiling = Shape(100,100,green)
        ceiling.set_position([x,0])

    for y in range(100, 500, 100):
        left = Shape(100,100,green)
        left.set_position([0,y])

        right = Shape(100,100,green)
        right.set_position([900,y])


    return Element.all_elements


def main():
    surface, res = setup()

    element_list = generate_elements()

    #pygame stuff
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
                    selected_element_id = selected_element_id + 1 % len(element_list)
                    selected_element = element_list[selected_element_id]
        key = pygame.key.get_pressed()
        if selected_element.element_type == "dir_light":
            if key[K_RIGHT]:
                dir_var = selected_element.get_direction_in_radians() - 0.2 % 6.2
                selected_element.set_direction(dir_var)
            elif key[K_LEFT]:
                dir_var = selected_element.get_direction_in_radians() + 0.2 % 6.2
                selected_element.set_direction(dir_var)
        else:
            if key[K_RIGHT]:
                selected_element.set_position([selected_element.get_position()[0] + 3, selected_element.get_position()[1]])
            elif key[K_LEFT]:
                selected_element.set_position([selected_element.get_position()[0] - 3, selected_element.get_position()[1]])
            elif key[K_UP]:
                selected_element.set_position([selected_element.get_position()[0], selected_element.get_position()[1] - 3])
            elif key[K_DOWN]:
                selected_element.set_position([selected_element.get_position()[0], selected_element.get_position()[1] + 3])

        draw(program,Shape.all_shapes, DirectionalLight.all_dir_lights, PointLight.all_point_lights)


main()


