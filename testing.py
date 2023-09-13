import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

def draw_cylinder(radius, height, num_slices):
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.0, height)
    for i in range(num_slices + 1):
        angle = i * 2.0 * 3.14159 / num_slices
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, height)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, 0.0, 0.0)
    for i in range(num_slices + 1):
        angle = i * 2.0 * 3.14159 / num_slices
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0.0)
    glEnd()

    glBegin(GL_TRIANGLE_STRIP)
    for i in range(num_slices + 1):
        angle = i * 2.0 * 3.14159 / num_slices
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3f(x, y, 0.0)
        glVertex3f(x, y, height)
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glTranslatef(0.0, 0.0, -5)

    glRotatef(45, 1, 1, 0)

    num_slices = 20
    radius = 0.5
    height = 1.0
    draw_cylinder(radius, height, num_slices)

    pygame.display.flip()
    pygame.time.wait(5000)

if __name__ == '__main__':
    main()
    draw_cylinder()
