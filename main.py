import sys
import pygame
import numpy as np
import random

from OpenGL.GL import *
from pygame.locals import *
from OpenGL.arrays import vbo
from helperClasses import *
from Renderer import *
from DeferredRenderer import *

red = "red"
green = "green"
blue = "blue"
white = "white"
def generate_color(color):
    bind_value = 0.0        #difference in color to original. (0 - 1) 0 being exactly requested color and 1 being up to very not the same color
    if color == "red":
        return (1, random.uniform(0, bind_value), random.uniform(0, bind_value), 0)
    elif color == "green":
        return (random.uniform(0, bind_value), 1, random.uniform(0, bind_value), 0)
    elif color == "blue":
        return (random.uniform(0, bind_value), random.uniform(0, bind_value), 1, 0)
    elif color == "white":
        return (1 - random.uniform(0, bind_value), 1 - random.uniform(0, bind_value), 1 - random.uniform(0, bind_value), 0)
    else:
        return (0, 0, 0, 0)


def generate_elements():
    dir_light = DirectionalLight([0.4,0.6],generate_color(white), 1)
    point_light = PointLight([250,250],generate_color(white),1)
    spot_light = SpotLight([750,250], [0.0,1.0], generate_color(white),1)

    for x in range(0, 1000, 100):
        floor = Shape(100,100,generate_color(green))
        floor.set_position([x,500])

        ceiling = Shape(100,100,generate_color(blue))
        ceiling.set_position([x,0])

    for y in range(100, 500, 100):
        left = Shape(100,100,generate_color(red))
        left.set_position([0,y])

        right = Shape(100,100,generate_color(white))
        right.set_position([900,y])


    return Element.all_elements


def tuple_to_array(tuple):
    a, b = tuple
    return [a, b]


def main():
    renderer = DeferredRenderer()

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
                    selected_element_id = (selected_element_id + 1) % len(element_list)
                    selected_element = element_list[selected_element_id]
            if pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                selected_element.set_position(tuple_to_array(mouse_pos))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    if selected_element.is_light():
                        selected_element.set_intensity(selected_element.get_intensity() + 0.05)
                        if selected_element.get_intensity() > 5:
                            selected_element.set_intensity(5)
                        elif selected_element.get_intensity() < 0:
                            selected_element.set_intensity(0)
                elif event.button == 5:
                    if selected_element.is_light():
                        selected_element.set_intensity(selected_element.get_intensity() - 0.05)
                        if selected_element.get_intensity() > 5:
                            selected_element.set_intensity(5)
                        elif selected_element.get_intensity() < 0:
                            selected_element.set_intensity(0)
        key = pygame.key.get_pressed()
        if selected_element.element_type == "dir_light" or selected_element.element_type == "spot_light":
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


