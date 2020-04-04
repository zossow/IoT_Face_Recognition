import RPi.GPIO as GPIO
import time
import threading

RED_LED = 36
YELLOW_LED = 38
GREEN_LED = 40


class LED(threading.Thread):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    def __init__(self, gpiopin, time):
        threading.Thread.__init__(self)
        self.gpiopin = gpiopin
        self.time = time

    def run(self):
        GPIO.setup(self.gpiopin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(self.gpiopin, GPIO.HIGH)
        time.sleep(self.time)
        GPIO.output(self.gpiopin, GPIO.LOW)

    @classmethod
    def cleanup(cls):
        GPIO.cleanup()


def main():
    t1 = LED(RED_LED, 1)
    t1.start()
    t2 = LED(GREEN_LED, 3)
    t2.start()

    t1.join()
    t2.join()

    GPIO.cleanup()


if __name__ == "__main__":
    main()
