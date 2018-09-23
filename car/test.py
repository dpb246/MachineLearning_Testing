'''
THIS TESTS:
making cars from randomly generated ones
stall detection

KNOWN ISSUES:
Improve random generation
Improve stall detection, gets stuck cycling on ramp
Camera will teleport around, # IDEA: Add smooth transition to new car

TODO:
Add random terrain addition
'''
from ult import *
from car_data import *
import pygame
import time
from pygame.locals import (QUIT, KEYDOWN, K_ESCAPE)
import random
from Box2D import * # The main library
# Box2D.b2 maps Box2D.b2Vec2 to vec2 (and so on)
from Box2D.b2 import (world, polygonShape, circleShape, edgeShape, staticBody, dynamicBody)
import UIEngine

# --- constants ---
# Box2D deals with meters, but we want to display pixels,
# so define a conversion factor:
PPM = 20.0  # pixels per meter
TARGET_FPS = 120
TIME_STEP = 1.0 / 60
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
XOFFSET = 0
YOFFSET = SCREEN_HEIGHT

# --- pygame setup ---
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('TESTS')
clock = pygame.time.Clock()

#UI
UI = UIEngine.UIScreen()
font = pygame.font.SysFont('Arial', 30)
UI.add_text((10, 10), font, "DEMO")

# --- pybox2d world setup ---
# Create the world
world = world(gravity=(0, -10), doSleep=True)

# The ground -- create some terrain
ground = world.CreateStaticBody(
    shapes=b2EdgeShape(vertices=[(-20, 0), (10, 0)])
)
blocker = world.CreateStaticBody( #Prevents cars from driving too far to the left
    position=(-18, 10),
    shapes=b2PolygonShape(box=(2,10))
)
x, y1, dx = 10, 0, 4
vertices = [0.25, 1, 4, 0, 0, -1, -2, -2, -1.25, 0]
def add_ground():
    global x, y1, dx
    print("Adding")
    for y2 in [i+random.random()+random.random() for i in vertices*2]:  # iterate through vertices multiple times
        ground.CreateEdgeFixture(
            vertices=[(x, y1), (x + dx, y2)],
            density=0,
            friction=0.1,
        )
        y1 = y2
        x += dx
add_ground()

cars = []
spawn = point(0, 4)
def make_car(c):
    # Create a car with 2 wheels
    box = world.CreateDynamicBody(
        position=spawn(),
        fixtures=b2FixtureDef(
            shape=b2PolygonShape(box=c.body.box),
            friction=c.body.friction,
            density=c.body.density,
            filter=b2Filter(
                groupIndex=-1,
                categoryBits=0x0002,
                maskBits=0xFFFF^0x0002,
            )
        )
    )
    wheels = []
    springs = []

    for w in c.wheels:
        wheel = world.CreateDynamicBody(
            position=(spawn+w.pos)(),
            fixtures=b2FixtureDef(
                shape=b2CircleShape(radius=w.radius),
                friction=w.friction,
                density=w.density,
                filter=b2Filter(
                    groupIndex=-1,
                    categoryBits=0x0002,
                    maskBits=0xFFFF,
                )
            )
        )
        wheels.append(wheel)
        spring = world.CreateWheelJoint(
                    bodyA=box,
                    bodyB=wheel,
                    anchor=wheel.position,
                    axis=(0.0, 1.0),
                    motorSpeed=w.motorSpeed,
                    maxMotorTorque=50,
                    enableMotor=True,
                    frequencyHz=w.frequencyHz,
                    dampingRatio=w.dampingRatio
                )
        springs.append(spring)
    cars.append([box, wheels, springs])

car1 = car()
car1.wheels[0].pos = point(1.25, -1)
car1.wheels[1].pos = point(-1.25, -1)
car1.wheels[0].radius = 1
car1.wheels[1].radius = 1
print("Car 1:\n"+str(car1))
make_car(car1)
car2 = car()
car2.wheels[0].pos = point(1.5, -1)
car2.wheels[1].pos = point(-1.5, -1)
car2.wheels[0].radius = 1.5
car2.wheels[1].radius = 1.5
print("Car 2:\n"+str(car2))
make_car(car2)
car3 = car()
car3.randomize()
print("Car 3:\n"+str(car3))
make_car(car3)
#Finds and returns the distance and index of the car that has travelled the farthest in the positive x direction
def find_farthest(cars):
    max_dis = 0
    index = 0
    for i in range(len(cars)):
        if cars[i][0].position.x > max_dis:
            max_dis = cars[i][0].position.x
            index = i
    return max_dis, index

#DRAWING
colors = {
    dynamicBody: (255, 255, 255, 255),
    staticBody: (0, 127, 127, 255),
}
def my_draw_polygon(polygon, body, fixture):
    vertices = [(body.transform * v) * PPM for v in polygon.vertices]
    vertices = [(v[0]+XOFFSET, YOFFSET - v[1]) for v in vertices]
    pygame.draw.polygon(screen, colors[body.type], vertices)
polygonShape.draw = my_draw_polygon

def my_draw_circle(circle, body, fixture):
    position = body.transform * circle.pos * PPM
    position = (position[0]+XOFFSET, YOFFSET - position[1])
    pygame.draw.circle(screen, colors[body.type], [int(
        x) for x in position], int(circle.radius * PPM))
circleShape.draw = my_draw_circle

def fix_vertices(vertices):
        return [(int(XOFFSET + v[0]), int(YOFFSET-v[1]))
                for v in vertices]
def _draw_edge(edge, body, fixture):
        vertices = fix_vertices([body.transform * edge.vertex1 * PPM,
                                 body.transform * edge.vertex2 * PPM])
        pygame.draw.line(screen, colors[body.type], vertices[0], vertices[1], 5)
edgeShape.draw = _draw_edge

# --- main game loop ---
running = True
stall_count = 0
last_pos = point(0, 0)
while running:
    # Check the event queue
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # The user closed the window or pressed escape
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            UI.clicks(pygame.mouse.get_pos()) #Check if any of the buttons were pressed
    screen.fill((0, 0, 0, 0))
    UI.draw(screen)
    # Draw the world
    for body in world.bodies:
        for fixture in body.fixtures:
            fixture.shape.draw(body, fixture)

    #Find the car that has travelled the farthest in the x+ direction
    farthest_dist, index = find_farthest(cars)

    #Check for stall on farthest car
    if stall_count > 10:
        stall_count = 0
        cars.pop(index)
        if len(cars) < 1: #No more cars, exit
            print("ending")
            time.sleep(0.25)
            running = False
            break
    elif abs(last_pos-point(*cars[index][0].position)) < 0.0005: #Could make this a smaller value
        stall_count += 1
    else:
        stall_count = 0
    last_pos = point(*cars[index][0].position)

    # Make Box2D simulate the physics of our world for one step.
    world.Step(TIME_STEP, 10, 10)
    #Check if car is about to run out of ground to drive on
    if x < farthest_dist+30:
        add_ground()
    #Have screen follow the car
    XOFFSET = (-farthest_dist) * PPM + SCREEN_WIDTH // 2
    YOFFSET = (cars[index][0].position[1]) * PPM + SCREEN_HEIGHT // 2

    # Flip the screen and try to keep at the target FPS
    pygame.display.flip()
    clock.tick(TARGET_FPS)

pygame.quit()
print('Done!')
