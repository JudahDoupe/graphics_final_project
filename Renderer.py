import sys
import pygame
import numpy as np

from math import sin, cos
from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo
from helperClasses import *


class Renderer:

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

    def __init__(self):
        pygame.init()
        infoObject = pygame.display.Info()
        width  = infoObject.current_w
        height = infoObject.current_h
        surface = pygame.display.set_mode((width, height), DOUBLEBUF|OPENGL)

         # Request a program and shader slots from GPU
        self.program  = glCreateProgram()
        vertex   = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)

        # Set shaders source
        glShaderSource(vertex, self.vertex_code)
        glShaderSource(fragment, self.fragment_code)

        # Compile shaders
        glCompileShader(vertex)
        glCompileShader(fragment)

        # Attach shader objects to the program
        glAttachShader(self.program, vertex)
        glAttachShader(self.program, fragment)

        # Build program
        glLinkProgram(self.program)


    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glUseProgram(self.program)

        resolutionLocation = glGetUniformLocation(self.program, "u_resolution")
        w, h = pygame.display.get_surface().get_size()
        glUniform2f(resolutionLocation, w, h)

        self.setup_dir_lights(DirectionalLight.all_dir_lights)

        self.setup_point_lights(PointLight.all_point_lights)


        for shape in Shape.all_shapes:
            position_buffer = shape.pos_vbo()
            position_buffer.bind()
            position_loc = glGetAttribLocation(self.program, 'a_positionP')
            glEnableVertexAttribArray(position_loc)
            glVertexAttribPointer(position_loc, 2, GL_FLOAT, False, 0, position_buffer )

            color_buffer = shape.color_vbo()
            color_buffer.bind()
            color_loc = glGetAttribLocation(self.program, 'a_color')
            glEnableVertexAttribArray(color_loc)
            glVertexAttribPointer(color_loc, 4, GL_FLOAT, False, 0, color_buffer )

            normal_buffer = shape.normal_vbo()
            normal_buffer.bind()
            normal_loc = glGetAttribLocation(self.program, 'a_normalV')
            glEnableVertexAttribArray(normal_loc)
            glVertexAttribPointer(normal_loc, 2, GL_FLOAT, False, 0, normal_buffer )

            translation_loc = glGetUniformLocation(self.program, 'u_translationV')
            glUniform2fv(translation_loc, 1, shape.get_position())
            glDrawArrays(GL_TRIANGLES, 0, shape.num_tris() * 3)

        pygame.display.flip()
        pygame.time.wait(10)


    def setup_dir_lights(self, dir_lights):
        light_index = 0

        directionLocation = glGetUniformLocation(self.program, "u_directionalLightD")
        intensityLocation = glGetUniformLocation(self.program, "u_directionalLightIntensity")

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

        glUniform2fv(directionLocation, 3, np.array(directions,'f'))
        glUniform1fv(intensityLocation, 3, np.array(intensities,'f'))


    def setup_point_lights(self, point_light):
        light_index = 0

        positionLocation = glGetUniformLocation(self.program, "u_pointLightP")
        intensityLocation = glGetUniformLocation(self.program, "u_pointLightIntensity")

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
