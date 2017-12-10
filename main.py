import sys
import pygame
import numpy as np

from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo
from helperClasses import *
from Renderer import *
from DeferredRenderer import *

red = [1, 0.2, 0.3, 0]
green = [0.2, 1, 0.3, 0]
blue = [0.3, 0.5, 1, 0]
white = [1, 1, 1, 0]


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
    renderer = DefferedRenderer()

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

        renderer.draw()


main()


