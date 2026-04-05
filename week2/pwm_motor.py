#!/usr/bin/env python3
#manual tuning of motor PWM parameters for E116 car
# steering PWM is tuned in another program, thus all servo pwm lines are commented out
#sample outputs for freq = 200

#motor_forward_start: 30.67
#motor_backward_start: 28.71

import RPi.GPIO as GPIO
import time

#PWM PINs on Jetson GPIO
#servo_pin = 15
motor_pin = 33

init_freq = 200
init_duty = 14.85*2
step_size = 0.01


def main():
    servo_duty = init_duty
    motor_duty = init_duty

    # Pin Setup:
    # Board pin-numbering scheme
    GPIO.setmode(GPIO.BOARD)
    # set pin as an output pin with optional initial state of HIGH
    #GPIO.setup(servo_pin, GPIO.OUT, initial=GPIO.HIGH)
    # p = GPIO.PWM(pin_number, frequency)
    #servo_pwm = GPIO.PWM(servo_pin, init_freq)
    
    GPIO.setup(motor_pin, GPIO.OUT, initial=GPIO.HIGH)
    motor_pwm = GPIO.PWM(motor_pin, init_freq)
    motor_pwm.start(motor_duty)
    
    print("This program helps to find the proper PWM ranges for E116 motor speed.\n")
    print("There are two parts of this test. For each part: ")
    print("Enter a number to change the PWM duty directly. The number must be between 27.00 --33.00.")
    print("Alternatively, enter one or more '+' to increase PWM by 0.1% per '+'. Enter one or more '-' to decrease PWM by 0.1% per '-'.\n" )
    print("When you find the critical value that start the motor, enter 'ok' to go to the next part.")
    
    print("================ Forward Speed ================")  
    print("Find the min duty that the motor starts forward, 'ok' to the next part.")
    motor_duty = init_duty
    motor_pwm.ChangeDutyCycle(motor_duty)
    print("Current motor duty: {}".format(motor_duty))
    
    while True:
        input_char = input()
        if input_char == "ok":
            break
        elif input_char[0] == '+':
            motor_duty += step_size * len(input_char)
        elif input_char[0] == '-':
            motor_duty -= step_size * len(input_char)
        else:
            try:
                motor_duty = float(input_char)
            except:
                print("!!!WRONG INPUT!!!")
        motor_pwm.ChangeDutyCycle(motor_duty)
        time.sleep(0.6) #stop the car after 0.6 second
        motor_pwm.ChangeDutyCycle(init_duty)
        print("Current motor duty: {}".format(motor_duty))
    motor_forward = motor_duty
    
    print("================ Backward Speed ================")
    print("Find the max duty that the motor starts backward, 'ok' to end.")
    motor_duty = init_duty
    motor_pwm.ChangeDutyCycle(motor_duty)
    print("Current motor duty: {}".format(motor_duty))
    
    while True:
        input_char = input()
        if input_char == "ok":
            break
        elif input_char[0] == '+':
            motor_duty += step_size * len(input_char)
        elif input_char[0] == '-':
            motor_duty -= step_size * len(input_char)
        else:
            try:
                motor_duty = float(input_char)
            except:
                print("!!!WRONG INPUT!!!")
        motor_pwm.ChangeDutyCycle(-motor_duty)
        time.sleep(0.6) #stop the car after 0.6 second
        motor_pwm.ChangeDutyCycle(init_duty)
        print("Current motor duty: {}".format(motor_duty))
    motor_backward = motor_duty
    
    print("================ Motor PWM Results ================")
    #print("servo_min: {}".format(servo_left))
    #print("servo_max: {}".format(servo_right))
    #print("servo_init: {}".format(servo_center))
    print("motor_forward_start: {}".format(motor_forward))
    print("motor_backward_start: {}".format(motor_backward))
    print("Note the numbers and they will be entered in pwm.yaml.") 
    print("================ End of Results ================")
    
    motor_pwm.stop()
        

if __name__ == '__main__':
    try: 
        main()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

