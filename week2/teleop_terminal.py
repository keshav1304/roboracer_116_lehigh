#!/usr/bin/python3
import RPi.GPIO as GPIO
import curses
import time

# --- GPIO Setup ---
GPIO.setmode(GPIO.BOARD)

servo_pin = 15
motor_pin = 33
deadman_pin = 40
freq = 200
Duty = 30

GPIO.setup(servo_pin, GPIO.OUT, initial=GPIO.HIGH)
servo_pwm = GPIO.PWM(servo_pin, freq) 
servo_pwm.start(Duty)

GPIO.setup(motor_pin, GPIO.OUT, initial=GPIO.HIGH)
motor_pwm = GPIO.PWM(motor_pin, freq)
motor_pwm.start(Duty)

GPIO.setup(deadman_pin, GPIO.IN)

def main(stdscr):
    # Curses Setup
    curses.curs_set(0)       # Hide the cursor
    stdscr.nodelay(True)     # Don't wait for user to press Enter
    stdscr.timeout(50)       # Check for keys every 50ms
    
    speed = 0
    angle = 0
    
    while True:
        # 1. Check Deadman Switch
        deadman_active = GPIO.input(deadman_pin)
        
        # 2. UI Display
        stdscr.clear()
        stdscr.addstr(0, 0, "=== JETSON TERMINAL CONTROL ===")
        stdscr.addstr(1, 0, "Use WASD to drive, 'Q' to quit.")
        status = "ACTIVE" if deadman_active else "HALTED (Deadman Switch)"
        stdscr.addstr(3, 0, f"Status: {status}")
        stdscr.addstr(4, 0, f"Speed: {Duty + speed} | Angle: {Duty + angle}")

        # 3. Get Key Input
        key = stdscr.getch()
        
        if key == ord('q'):
            break
            
        # Control Logic
        if key == ord('w'):
            speed = 2
        elif key == ord('s'):
            speed = -2
        else:
            speed = 0 # Stop if W/S not pressed
            
        if key == ord('a'):
            angle = -2
        elif key == ord('d'):
            angle = 2
        else:
            angle = 0 # Straight if A/D not pressed

        # 4. Apply PWM
        # Only move if deadman switch allows it
        if deadman_active:
            servo_pwm.ChangeDutyCycle(Duty + angle)
            motor_pwm.ChangeDutyCycle(Duty + speed)
        else:
            servo_pwm.ChangeDutyCycle(Duty)
            motor_pwm.ChangeDutyCycle(Duty)

        stdscr.refresh()

# Run the curses application
try:
    curses.wrapper(main)
finally:
    # Cleanup
    servo_pwm.stop()
    motor_pwm.stop()
    GPIO.cleanup()
    print("Program terminated safely.")
