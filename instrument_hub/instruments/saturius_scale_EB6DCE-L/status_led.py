# led_blink.py
import sys
import time
from gpiozero import LED

# Setup for GPIO pin 16
LED_PIN_GREEN = 20
LED_PIN_BLUE = 16
LED_PIN_RED = 21

# Create LED objects
led_green = LED(LED_PIN_GREEN)
led_blue = LED(LED_PIN_BLUE)
led_red = LED(LED_PIN_RED)

LED_MAPPER = {"green": led_green, "blue": led_blue, "red": led_red}
standby_turned_on = False


def blink_led(led, duration: float, count: int):
    for i in range(count):
        led.on()
        time.sleep(duration)
        led.off()
        if i + 1 != count:
            time.sleep(duration)


def standby_on():
    global standby_turned_on
    led_blue.on()
    standby_turned_on = True


def standby_off():
    global standby_turned_on
    led_blue.off()
    standby_turned_on = False


try:
    print("LED control started")
    while True:
        # Wait for input from the parent process
        command = sys.stdin.readline().strip()
        if command == "standby_on":
            standby_on()
            print("Standby is turned on")
        elif command == "standby_off":
            standby_off()
            print("Standby is turned off")
        else:
            if standby_turned_on:
                standby_off()
                color, duration, count = command.split("_")
                blink_led(
                    led=LED_MAPPER[color], duration=float(duration), count=int(count)
                )
                standby_on()
            else:
                color, duration, count = command.split("_")
                blink_led(
                    led=LED_MAPPER[color], duration=float(duration), count=int(count)
                )

except KeyboardInterrupt:
    print("LED control stopped")
finally:
    for led in LED_MAPPER.values():
        led.off()
