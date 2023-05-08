from gpiozero import PWMLED
from time import sleep
#from signal import pause

led = PWMLED(12)

while True:
    for val in range(101):
        led.value = val / 100
        sleep(0.01)
    
    for val in range(100, -1, -1):
        led.value = val / 100
        sleep(0.01)

'''import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

ledpin = 12

GPIO.setup(ledpin, GPIO.OUT)
led_pwm = GPIO.PWM(ledpin, 1000)
led_pwm.start(0)

while True:
    for duty in range(101):
        led_pwm.ChangeDutyCycle(duty)
        sleep(0.01)
    
    sleep(0.5)
    
    for duty in range(100, -1, -1):
        led_pwm.ChangeDutyCycle(duty)
        sleep(0.01)
    
    sleep(0.5)'''