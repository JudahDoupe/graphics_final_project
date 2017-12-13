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

##### GEOMETRY SHADER #####

    geomenty_vertex_code = """
        uniform vec2 u_resolution;

        attribute vec2 a_positionP;
        attribute vec2 a_normalV;
        attribute vec4 a_color;

        uniform vec2 u_translationV;
        uniform vec2 u_cameraP;

        varying vec2 v_positionP;
        varying vec2 v_normalV;
        varying vec4 v_color;

        void main() {
            vec2 positionP = a_positionP + u_translationV - (u_cameraP - (u_resolution / 2));
            vec2 clipSpaceP = (((positionP/ u_resolution) * 2 ) - 1 ) * vec2(1, -1);

            v_positionP = positionP / u_resolution;
            v_normalV = (a_normalV + 1) / 2;
            v_color = a_color;

            gl_Position = vec4(clipSpaceP , 0, 1);
        }
    """
    geomenty_fragment_code = """
        precision highp float;

        varying vec2 v_positionP;
        varying vec2 v_normalV;
        varying vec4 v_color;

        void main() {
            gl_FragData[0] = vec4(v_positionP,0,0);
            gl_FragData[1] = vec4(v_normalV,0,0);
            gl_FragData[2] = v_color;
        }
    """

##### LIGHTING SHADERS #####

    lighting_vertex_code = """
        attribute vec2 a_positionP;

        void main()
        {
               gl_Position = vec4(a_positionP, 0, 1);
        }
    """
    point_light_fragment_code = """
        uniform vec4 u_LightColor;
        uniform vec2 u_LightPosition;
        uniform float u_LightIntensity;

        uniform vec2 u_resolution;
        uniform vec2 u_cameraP;
        uniform sampler2D gPositionMap;
        uniform sampler2D gColorMap;
        uniform sampler2D gNormalMap;
        uniform sampler2D gShadowMap;

        void main()
        {
               vec2 WorldCoord = gl_FragCoord.xy - (u_cameraP - (u_resolution / 2));
               vec2 CenteredCoord = (gl_FragCoord.xy - (u_resolution / 2)) * vec2(1,-1);
               vec2 ScreenCoord = CenteredCoord + (u_resolution / 2);
               vec2 TexCoord = gl_FragCoord.xy / u_resolution;

               vec2 WorldPos = texture(gPositionMap, TexCoord).xy * u_resolution;
               vec4 Color = texture(gColorMap, TexCoord).xyzw;
               vec2 Normal = (texture(gNormalMap, TexCoord).xy * 2) - 1;

               vec2 LightPosition = u_LightPosition - (u_cameraP - (u_resolution / 2));
               vec2 LightVector = LightPosition - ScreenCoord;
               vec2 LightDirection = normalize(LightVector);
               float LightDistance = length( LightVector );
               float LightFraction = dot( Normal, LightDirection);
               vec2 LightReflectedDirection = normalize( Normal - LightDirection * 2);
               float Attenuation = u_LightIntensity / (u_LightIntensity+ (pow( LightDistance, 2) / 30000));

               vec4 SpecularColor = u_LightColor * pow( max( 0, dot( normalize(-CenteredCoord), LightReflectedDirection )), 10);



               float visible = 0;
               float MaxDistance = texture(gShadowMap, TexCoord).x * u_resolution.y;
               if( LightDistance <= MaxDistance){
                   visible = 1;
               }


               if(WorldPos == vec2(0,0)){
                   gl_FragColor = u_LightColor * Attenuation * visible;
               }else{
                   gl_FragColor = (Color + SpecularColor) * u_LightColor * LightFraction * Attenuation * visible;
               }
        }
    """
    directional_light_fragment_code = """
        uniform vec4 u_LightColor;
        uniform vec2 u_LightDirection;
        uniform float u_LightIntensity;

        uniform vec2 u_resolution;
        uniform vec2 u_cameraP;
        uniform sampler2D gColorMap;
        uniform sampler2D gNormalMap;

        void main()
        {
               vec2 WorldCoord = gl_FragCoord.xy - (u_cameraP - (u_resolution / 2));
               vec2 CenteredCoord = (gl_FragCoord.xy - (u_resolution / 2)) * vec2(1,-1);
               vec2 ScreenCoord = CenteredCoord + (u_resolution / 2);
               vec2 TexCoord = gl_FragCoord.xy / u_resolution;

               vec4 Color = texture(gColorMap, TexCoord).xyzw;
               vec2 Normal = (texture(gNormalMap, TexCoord).xy * 2) - 1;

               vec2 LightDirection = -u_LightDirection;
               float LightFraction = dot( Normal, LightDirection);
               vec2 LightReflectedDirection = normalize( Normal - LightDirection * 2);

               vec4 SpecularColor = u_LightColor * pow( max( 0, dot( normalize(-CenteredCoord), LightReflectedDirection )), 10);

               gl_FragColor = Color  * u_LightColor * LightFraction;
        }
    """
    spot_light_fragment_code = """
        uniform vec4 u_LightColor;
        uniform vec2 u_LightPosition;
        uniform vec2 u_LightDirection;
        uniform float u_LightIntensity;

        uniform vec2 u_resolution;
        uniform vec2 u_cameraP;
        uniform sampler2D gPositionMap;
        uniform sampler2D gColorMap;
        uniform sampler2D gNormalMap;
        uniform sampler2D gShadowMap;

        void main()
        {
               vec2 WorldCoord = gl_FragCoord.xy - (u_cameraP - (u_resolution / 2));
               vec2 CenteredCoord = (gl_FragCoord.xy - (u_resolution / 2)) * vec2(1,-1);
               vec2 ScreenCoord = CenteredCoord + (u_resolution / 2);
               vec2 TexCoord = gl_FragCoord.xy / u_resolution;

               vec2 WorldPos = texture(gPositionMap, TexCoord).xy * u_resolution;
               vec4 Color = texture(gColorMap, TexCoord).xyzw;
               vec2 Normal = (texture(gNormalMap, TexCoord).xy * 2) - 1;

               vec2 LightPosition = u_LightPosition - (u_cameraP - (u_resolution / 2));
               vec2 LightVector = LightPosition - ScreenCoord;
               vec2 LightDirection = normalize(LightVector);
               float LightDistance = length( LightVector );
               vec2 LightCoord = LightPosition / u_resolution;
               float LightFraction = dot( Normal, LightDirection);
               vec2 LightReflectedDirection = normalize( Normal - LightDirection * 2);
               float Attenuation = u_LightIntensity / (u_LightIntensity+ (pow( LightDistance, 2) / 30000));

               vec4 SpecularColor = u_LightColor * pow( max( 0, dot( normalize(-CenteredCoord), LightReflectedDirection )), 10);

               float visible = 0;
               float theta = atan(LightDirection.y, LightDirection.x);
               float coord = (theta + 3.14) / (2.0*3.14);
               float MaxDistance = texture(gShadowMap, vec2(coord,0)).x * u_resolution.y;
               if( dot( LightDirection, -u_LightDirection) > 0.75 || LightDistance <= MaxDistance){
                   visible = 1;
               }

               if(WorldPos == vec2(0,0)){
                   gl_FragColor = u_LightColor * Attenuation * visible;
               }else{
                   gl_FragColor = (Color + SpecularColor) * u_LightColor * LightFraction * Attenuation * visible;
               }
        }
    """

##### SHADOW SHADER #####

    shadow_fragment_code  = """
        uniform sampler2D occlusion_texture;
        uniform vec2 u_resolution;
        uniform vec2 u_lightPosition;
        uniform vec2 u_cameraP;

        void main(void) {
            float min_distance = 1.0;

            vec2 TexCoord = gl_FragCoord.xy / u_resolution;
            vec2 LightPosition = u_lightPosition - (u_cameraP - (u_resolution / 2));
            vec2 LightCoord = LightPosition / u_resolution;

            for (float y=0.0; y < u_resolution.y; y+=1.0) {

                float distance = y / u_resolution.y;

                float theta = 3.14 * 1.5 + (TexCoord.x * 2 - 1) * 3.14;
                float r = (1.0 + (distance * 2 - 1)) * 0.5;
                vec2 coord = vec2(-r * sin(theta) * 0.5, -r * cos(theta) * 0.5) + LightCoord;
                coord = clamp(coord, vec2(0,0), vec2(1,1));

                vec2 data = texture2D(occlusion_texture, coord).xy;

                if (data != vec2(0,0)) {
                    min_distance = min(min_distance, distance);
                }
            }
            gl_FragData[3] = vec4(vec3(min_distance), 1.0);
        }
    """



    def __init__(self):
        pygame.init()
        infoObject = pygame.display.Info()
        self.width  = infoObject.current_w
        self.height = infoObject.current_h
        self.camera_position = [self.width/2,self.height/2]
        self.surface = pygame.display.set_mode((self.width, self.height), DOUBLEBUF|OPENGL)

        self.geomenty_program  = self.create_program(self.geomenty_vertex_code, self.geomenty_fragment_code)
        self.point_light_program  = self.create_program(self.lighting_vertex_code, self.point_light_fragment_code)
        self.spot_light_program  = self.create_program(self.lighting_vertex_code, self.spot_light_fragment_code)
        self.directional_light_program  = self.create_program(self.lighting_vertex_code, self.directional_light_fragment_code)
        self.shadow_program  = self.create_program(self.lighting_vertex_code, self.shadow_fragment_code)

        self.geomenty_buffer = GBuffer(self.width, self.height)


    def draw(self):
        self.geomenty_buffer.bind()
        self.render_geometry()
        self.geomenty_buffer.unbind()

        self.geomenty_buffer.bind_for_reading()
        glEnable(GL_BLEND);
        glBlendEquation(GL_FUNC_ADD);
        glBlendFunc(GL_ONE, GL_ONE);
        glClear(GL_COLOR_BUFFER_BIT);

        self.render_point_lights()
        self.render_spot_lights()
        self.render_directional_lights()

        pygame.display.flip()
        pygame.time.wait(10)


    def render_geometry(self):

        glUseProgram(self.geomenty_program)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_BLEND);


        res_loc = glGetUniformLocation(self.geomenty_program, "u_resolution")
        camera_loc = glGetUniformLocation(self.geomenty_program, 'u_cameraP')

        glUniform2f(res_loc, self.width, self.height)
        glUniform2fv(camera_loc, 1, self.camera_position)

        for shape in Shape.all_shapes:

            position_buffer = shape.pos_vbo()
            color_buffer = shape.color_vbo()
            normal_buffer = shape.normal_vbo()

            self.assign_attribute(self.geomenty_program, 'a_positionP', position_buffer, 2)
            self.assign_attribute(self.geomenty_program, 'a_color', color_buffer, 4)
            self.assign_attribute(self.geomenty_program, 'a_normalV', normal_buffer, 2)

            transform_loc = glGetUniformLocation(self.geomenty_program, 'u_translationV')
            glUniform2fv(transform_loc, 1, shape.get_position())

            glDrawArrays(GL_TRIANGLES, 0, shape.num_tris() * 3)


    def render_point_lights(self):

        glUseProgram(self.point_light_program)

        res_loc = glGetUniformLocation(self.point_light_program, "u_resolution")
        camera_loc = glGetUniformLocation(self.point_light_program, 'u_cameraP')

        glUniform2f(res_loc, self.width, self.height)
        glUniform2fv(camera_loc, 1, self.camera_position)

        #set texture data
        glUniform1i(glGetUniformLocation(self.point_light_program, "gPositionMap"), 0);
        glUniform1i(glGetUniformLocation(self.point_light_program, "gNormalMap"), 1);
        glUniform1i(glGetUniformLocation(self.point_light_program, "gColorMap"), 2);
        glUniform1i(glGetUniformLocation(self.point_light_program, "gShadowMap"), 3);

        for light in PointLight.all_point_lights:

            self.render_shadow_map(light.get_position())
            glUseProgram(self.point_light_program)

            position_loc = glGetUniformLocation(self.point_light_program, 'u_LightPosition')
            color_loc = glGetUniformLocation(self.point_light_program, 'u_LightColor')
            intensity_loc = glGetUniformLocation(self.point_light_program, 'u_LightIntensity')

            glUniform2fv(position_loc, 1, np.array(light.get_position(),'f'))
            glUniform4fv(color_loc, 1, np.array(light.get_color(),'f'))
            glUniform1f(intensity_loc, np.array(light.get_intensity(),'f'))

            quad = vbo.VBO(np.array([-1,-1, -1,1, 1,-1, 1,1, -1,1, 1,-1],'f'))
            self.assign_attribute(self.point_light_program, 'a_positionP', quad, 2)

            glDrawArrays(GL_TRIANGLES, 0, 6)

    def render_spot_lights(self):

        glUseProgram(self.spot_light_program)

        res_loc = glGetUniformLocation(self.spot_light_program, "u_resolution")
        camera_loc = glGetUniformLocation(self.spot_light_program, 'u_cameraP')

        glUniform2f(res_loc, self.width, self.height)
        glUniform2fv(camera_loc, 1, self.camera_position)

        #set texture data
        glUniform1i(glGetUniformLocation(self.spot_light_program, "gPositionMap"), 0);
        glUniform1i(glGetUniformLocation(self.spot_light_program, "gNormalMap"), 1);
        glUniform1i(glGetUniformLocation(self.spot_light_program, "gColorMap"), 2);
        glUniform1i(glGetUniformLocation(self.spot_light_program, "gShadowMap"), 3);

        for light in SpotLight.all_spot_lights:

            self.render_shadow_map(light.get_position())
            glUseProgram(self.spot_light_program)

            position_loc = glGetUniformLocation(self.spot_light_program, 'u_LightPosition')
            direction_loc = glGetUniformLocation(self.spot_light_program, 'u_LightDirection')
            color_loc = glGetUniformLocation(self.spot_light_program, 'u_LightColor')
            intensity_loc = glGetUniformLocation(self.spot_light_program, 'u_LightIntensity')

            glUniform2fv(position_loc, 1, np.array(light.get_position(),'f'))
            glUniform2fv(direction_loc, 1, np.array(light.get_direction(),'f'))
            glUniform4fv(color_loc, 1, np.array(light.get_color(),'f'))
            glUniform1f(intensity_loc, np.array(light.get_intensity(),'f'))

            quad = vbo.VBO(np.array([-1,-1, -1,1, 1,-1, 1,1, -1,1, 1,-1],'f'))
            self.assign_attribute(self.spot_light_program, 'a_positionP', quad, 2)

            glDrawArrays(GL_TRIANGLES, 0, 6)

    def render_directional_lights(self):
        glUseProgram(self.directional_light_program)

        res_loc = glGetUniformLocation(self.directional_light_program, "u_resolution")
        camera_loc = glGetUniformLocation(self.directional_light_program, 'u_cameraP')

        glUniform2f(res_loc, self.width, self.height)
        glUniform2fv(camera_loc, 1, self.camera_position)

        glUniform1i(glGetUniformLocation(self.directional_light_program, "gNormalMap"), 1);
        glUniform1i(glGetUniformLocation(self.directional_light_program, "gColorMap"), 2);

        for light in DirectionalLight.all_dir_lights:

            direction_loc = glGetUniformLocation(self.directional_light_program, 'u_LightDirection')
            color_loc = glGetUniformLocation(self.directional_light_program, 'u_LightColor')
            intensity_loc = glGetUniformLocation(self.directional_light_program, 'u_LightIntensity')

            glUniform2fv(direction_loc, 1, np.array(light.get_direction(),'f'))
            glUniform4fv(color_loc, 1, np.array(light.get_color(),'f'))
            glUniform1f(intensity_loc, np.array(light.get_intensity(),'f'))

            quad = vbo.VBO(np.array([-1,-1, -1,1, 1,-1, 1,1, -1,1, 1,-1],'f'))
            self.assign_attribute(self.directional_light_program, 'a_positionP', quad, 2)

            glDrawArrays(GL_TRIANGLES, 0, 6)


    def render_shadow_map(self, light_pos):
        self.geomenty_buffer.bind()
        glUseProgram(self.shadow_program)

        res_loc = glGetUniformLocation(self.shadow_program, "u_resolution")
        pos_loc = glGetUniformLocation(self.shadow_program, "u_lightPosition")
        camera_loc = glGetUniformLocation(self.directional_light_program, 'u_cameraP')

        glUniform2f(res_loc, self.width, self.height)
        glUniform2fv(camera_loc, 1, self.camera_position)
        glUniform2fv(pos_loc, 1, light_pos)
        glUniform1i(glGetUniformLocation(self.point_light_program, "occlusion_texture"), 0);

        quad = vbo.VBO(np.array([-1,-1, -1,1, 1,-1, 1,1, -1,1, 1,-1],'f'))
        self.assign_attribute(self.point_light_program, 'a_positionP', quad, 2)

        glDrawArrays(GL_TRIANGLES, 0, 6)
        self.geomenty_buffer.unbind()



##### BOILER PLATE FUNCTIONS #####

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

    def assign_attribute(self, program, name, vbo, size):
        vbo.bind()
        loc = glGetAttribLocation(program, name)
        glEnableVertexAttribArray(loc)
        glVertexAttribPointer(loc, size, GL_FLOAT, False, 0, vbo )
        vbo.unbind()


class GBuffer:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.fbo = glGenFramebuffers(1)

        self.position_texture = self.add_texture(0)
        self.normal_texture = self.add_texture(1)
        self.color_texture = self.add_texture(2)
        self.shadow_texture = self.add_texture(3)

        self.bind()
        glDrawBuffers(3, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2, GL_COLOR_ATTACHMENT3])

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("Failed To Create G-Buffer");

        self.unbind()

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

    def bind_for_reading(self):
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);

        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, self.position_texture)
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, self.normal_texture)
        glActiveTexture(GL_TEXTURE0 + 2)
        glBindTexture(GL_TEXTURE_2D, self.color_texture)
        glActiveTexture(GL_TEXTURE0 + 3)
        glBindTexture(GL_TEXTURE_2D, self.shadow_texture)


    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def add_texture(self, index):
        texture = glGenTextures(1)
        glPixelStorei(GL_PACK_ALIGNMENT,1)
        glBindTexture(GL_TEXTURE_2D, texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_FLOAT, None)

        self.bind()
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + index, GL_TEXTURE_2D, texture, 0)
        self.unbind()

        return texture
