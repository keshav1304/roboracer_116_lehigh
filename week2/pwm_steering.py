#!/usr/bin/env python3
#manual tuning of servo PWM duty for the E116 car to drive straight
#enter the motor PWM parameters on line 26 -27, othervise use the defauld values 
#motor_forward_start: 30.67 (31.1)
#motor_backward_start: 28.71 (28.8)
#with PWM freq=200

#sample outputs:
#servo_center: 29.7 #the duty for the car to drive straight


import RPi.GPIO as GPIO
import time

#PWM PINs on Jetson GPIO
servo_pin = 15
motor_pin = 33

init_freq = 200

servo_init=29.7
motor_init=29.7

## CHANGE motor_forward_start TO YOUR FOUND VALUE ##

motor_forward_start=30.11
motor_backward_start=29.11
speed=2.0

def main():
    
    Motor_Duty = motor_forward_start +speed
    Servo_Duty = servo_init
    
    # Pin Setup:
    # Board pin-numbering scheme
    GPIO.setmode(GPIO.BOARD)
    
    # set and start servo pin
    GPIO.setup(servo_pin, GPIO.OUT, initial=GPIO.HIGH)
    servo_pwm = GPIO.PWM(servo_pin, init_freq)
    servo_pwm.start(servo_init)
    
    # set and start motor pin
    GPIO.setup(motor_pin, GPIO.OUT, initial=GPIO.HIGH)
    motor_pwm = GPIO.PWM(motor_pin, init_freq)
    motor_pwm.start(motor_init)
      
       
    print("================ Part 1 ================")
    print("Current PWM duty for steering PWM:", Servo_Duty)
    print("Set the servo PWM for steering at the center, The number must be within 25.00 -- 34.00")
    print("Place the car on the floor and press 'S' to run the car.")
    print("Press 'ok' to finish setting.")  
    while True:
        input_char = input()
        if input_char == "ok":
            break
        elif input_char == "S":
            servo_pwm.ChangeDutyCycle(Servo_Duty)
            motor_pwm.ChangeDutyCycle(Motor_Duty)
            time.sleep(1.2) #stop the car after 0.6 second
            motor_pwm.ChangeDutyCycle(motor_init)
        else: 
            try:
                Servo_Duty = float(input_char)
                if Servo_Duty > 34.00 or Servo_Duty < 25.00: 
                    Servo_Duty = servo_init
                    print("!!!WRONG RANGE!!!")
            except:
                print("!!!WRONG INPUT!!!")
        servo_pwm.ChangeDutyCycle(Servo_Duty)
        print("Current servo duty: {}".format(Servo_Duty))
       
       

    servo_pwm.stop()
    motor_pwm.stop()
        

if __name__ == '__main__':
    try: 
        main()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

