#!/usr/bin/python3

'''
install the required package if not yet:
sudo pip3 install pygame

Make sure the ESC is powered. If running the car headless, then Use another linux computer to ssh into the Orin Nano with your team number replacing 06:
ssh -X team106@190.168.0.106
or 
ssh -X team306@190.168.0.106

Run teleop program with the following command:
python3 teleop.py

A small black window will popup. Click on the window and use 'WASD' keys for control:
W - Forward
A - Turn left
S - Backword
D - Trun right
'''

import RPi.GPIO as GPIO 
import pygame
GPIO.setmode(GPIO.BOARD)

# PWM Definitons:
servo_pin=15
motor_pin=33
freq = 200
Duty=30

GPIO.setup(servo_pin, GPIO.OUT, initial=GPIO.HIGH)
# p = GPIO.PWM(pin_number,frequency)
servo_pwm = GPIO.PWM(servo_pin,freq) 
servo_pwm.start(Duty)

GPIO.setup(motor_pin, GPIO.OUT, initial=GPIO.HIGH)
motor_pwm=GPIO.PWM(motor_pin,freq)
motor_pwm.start(Duty)

speed = 0
angle = 0

pygame.init()
X = 200
Y = 200
screen = pygame.display.set_mode((X, Y))
clock = pygame.time.Clock()
running = True
dt = 0
font = pygame.font.Font('freesansbold.ttf', 32)

DMtext = font.render('DM?', True, (128, 0, 0), (255,255,255))
DMtextRect = DMtext.get_rect()
DMtextRect.center = (X // 2, Y // 2)

# deadman pin Definitons:
deadman_pin = 40
GPIO.setup(deadman_pin, GPIO.IN)  # Pin set as input

while running:
    deadman_value = GPIO.input(deadman_pin)
    
    if deadman_value:
        screen.fill((0,0,0))
    else:
        screen.fill((255, 255, 255))
        screen.blit(DMtext, DMtextRect)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        speed = 2
    elif keys[pygame.K_s]:
        speed = -2
    else:
        speed = 0
    if keys[pygame.K_a]:
        angle = -2
    elif keys[pygame.K_d]:
        angle = 2
    else:
        angle = 0
    # print(speed)
    
    # both the servo and motor (ESC) take PWM inputs.
    # the servo will turn left when the duty cycle is less than "Duty"
    # the servo will turn right when the duty cycle is more than "Duty"
    
    # the car will run forward when the duty cycle is more than "Duty"
    # the car will run backward when the duty cycle is less than "Duty"
    
    # please limit dutycycle within (30-4, 30+4) to prevent damage.
    
    servo_pwm.ChangeDutyCycle(Duty+angle)
    motor_pwm.ChangeDutyCycle(Duty+speed)
    # flip() the display to put your work on screen
    #pygame.display.flip()
    pygame.display.update()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

servo_pwm.stop()
motor_pwm.stop()
GPIO.cleanup()  # cleanup all GPIO

