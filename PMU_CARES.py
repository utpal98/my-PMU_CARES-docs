import machine
import neopixel
import time
import random
import framebuf
from micropython import const
import machine

SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class OLED:
    def __init__(self, width=128, height=64, scl_pin=22, sda_pin=21, i2c_addr=0x3C, spi=None, external_vcc=False):
        """
        Initialize the OLED display using I2C (default) or SPI.

        Example:
        ```python
        oled = OLED()
        ```
        """
        pass

    def contrast(self, contrast):
        """
        Set the contrast level.

        Example:
        ```python
        oled = OLED()
        oled.contrast(128)
        ```
        """
        pass

    def write(self, text, x=0, y=0):
        """
        Write text on the OLED display at position (x, y).

        Example:
        ```python
        oled = OLED()
        oled.write("Hello, World!", 10, 10)
        ```
        """
        pass

    def clear(self):
        """
        Clear the display.

        Example:
        ```python
        oled = OLED()
        oled.clear()
        ```
        """
        pass

    def fill(self, color):
        """
        Fill the display with a single color (0 or 1).

        Example:
        ```python
        oled = OLED()
        oled.fill(1)
        ```
        """
        pass

    def poweroff(self):
        """
        Turn off the display.

        Example:
        ```python
        oled = OLED()
        oled.poweroff()
        ```
        """
        pass

    def poweron(self):
        """
        Turn on the display.

        Example:
        ```python
        oled = OLED()
        oled.poweron()
        ```
        """
        pass

    def invert(self, invert):
        """
        Invert display colors.

        Example:
        ```python
        oled = OLED()
        oled.invert(1)
        ```
        """
        pass

    def load_image(self, filename):
        """
        Load an image from a file.

        Example:
        ```python
        oled = OLED()
        image = oled.load_image("logo.bin")
        ```
        """
        pass

    def display_image(self, data):
        """
        Display image data on the screen.

        Example:
        ```python
        oled = OLED()
        image = oled.load_image("logo.bin")
        oled.display_image(image)
        ```
        """
        pass

    def fill_rect(self, x, y, w, h, color):
        """
        Draw a filled rectangle.

        Example:
        ```python
        oled = OLED()
        oled.fill_rect(10, 10, 40, 20, 1)
        ```
        """
        pass

    def vline(self, x, y, h, color):
        """
        Draw a vertical line.

        Example:
        ```python
        oled = OLED()
        oled.vline(5, 0, 30, 1)
        ```
        """
        pass

    def blit(self, framebuffer, x=0, y=0):
        """
        Copy framebuffer content to the display.

        Example:
        ```python
        dummy_fb = framebuf.FrameBuffer(bytearray(1024), 128, 64, framebuf.MONO_VLSB)
        oled = OLED()
        oled.blit(dummy_fb, 0, 0)
        ```
        """
        pass

    def display_image_from_bytes(self, image):
        """
        Display image from bytearray.

        Example:
        ```python
        image = bytearray(1024)
        oled = OLED()
        oled.display_image_from_bytes(image)
        ```
        """
        pass

class CARESpixel:
    def __init__(self, pin, total_leds):
        """
        Initialize the NeoPixel display.

        :param pin: A `machine.Pin` object or pin number (int).
        :param total_leds: Total number of LEDs in the matrix (max 64).

        Example:
            cp = CARESpixel(pin=5, total_leds=64)
        """
        if isinstance(pin, machine.Pin):
            self.pin = pin
        elif isinstance(pin, int):
            self.pin = machine.Pin(pin, machine.Pin.OUT)
        else:
            raise ValueError("Invalid pin. Must be machine.Pin or int.")

        if total_leds > 64:
            raise ValueError("total_leds cannot exceed 64.")

        self.total_leds = total_leds
        self.display = neopixel.NeoPixel(self.pin, self.total_leds)
        self.dim_purple = (29, 0, 42)
        self.dim_green = (0, 50, 0)
        self.bright_red = (50, 0, 0)
        self.cloud_color = (20, 20, 20)
        self.rain_color = (0, 0, 50)
        self.lightning_color = (255, 255, 0)
        self.slow_rain_delay = 0.15
        self.fast_rain_delay = 0.05

        self.snake = []
        self.food = []
        self.current_direction = (1, 0)

        self.letters = {
            'A': [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
            'B': [0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110],
            'C': [0b01111, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b01111],
            # ... (other letters omitted for brevity)
            ' ': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000]
        }

    def clear_display(self):
        """
        Clear all LEDs.

        Example:
            cp.clear_display()
        """
        for i in range(self.total_leds):
            self.display[i] = (0, 0, 0)
        self.display.write()

    def display_letter_with_offset(self, letter, offset):
        """
        Display a letter with horizontal offset (for scrolling).

        Example:
            cp.display_letter_with_offset('A', 2)
        """
        pattern = self.letters.get(letter.upper(), [])
        for row, row_data in enumerate(pattern):
            for col in range(5):
                matrix_col = col + offset
                if 0 <= matrix_col < 8:
                    if row_data & (1 << (4 - col)):
                        self.display[row * 8 + matrix_col] = self.dim_purple
                    else:
                        self.display[row * 8 + matrix_col] = (0, 0, 0)

    def scroll_text(self, text):
        """
        Scroll text across the LED matrix.

        Example:
            cp.scroll_text("HELLO")
        """
        text = ' ' + text + '  '
        for position in range(len(text) * 6):
            self.clear_display()
            for i, letter in enumerate(text):
                self.display_letter_with_offset(letter, 8 - (position - i * 6))
            self.display.write()
            time.sleep(0.1)

    # Snake game methods
    def reset_game(self):
        """
        Reset snake game state.

        Example:
            cp.reset_game()
        """
        self.snake = [(4, 4)]
        self.food = self.spawn_food()
        self.current_direction = (1, 0)

    def coord_to_index(self, x, y):
        """
        Convert x,y coordinates to LED index.

        Example:
            idx = cp.coord_to_index(2, 3)
        """
        return y * 8 + x

    def update_snake_display(self):
        """
        Update LEDs to show snake and food positions.

        Example:
            cp.update_snake_display()
        """
        self.clear_display()
        for segment in self.snake:
            self.display[self.coord_to_index(segment[0], segment[1])] = self.dim_green
        self.display[self.coord_to_index(self.food[0], self.food[1])] = self.bright_red
        self.display.write()

    def is_valid_position(self, position):
        """
        Check if a position is valid for the snake.

        Example:
            valid = cp.is_valid_position((1, 1))
        """
        x, y = position
        return 0 <= x < 8 and 0 <= y < 8 and position not in self.snake

    def spawn_food(self):
        """
        Generate a new food position.

        Example:
            food = cp.spawn_food()
        """
        while True:
            new_food = (random.randint(0, 7), random.randint(0, 7))
            if new_food not in self.snake:
                return new_food

    def get_direction_towards_food(self):
        """
        Determine snake direction towards food.

        Example:
            direction = cp.get_direction_towards_food()
        """
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food

        possible_directions = []
        if head_x < food_x:
            possible_directions.append((1, 0))
        elif head_x > food_x:
            possible_directions.append((-1, 0))
        if head_y < food_y:
            possible_directions.append((0, 1))
        elif head_y > food_y:
            possible_directions.append((0, -1))

        for direction in possible_directions:
            next_pos = (head_x + direction[0], head_y + direction[1])
            if self.is_valid_position(next_pos):
                return direction

        for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            next_pos = (head_x + direction[0], head_y + direction[1])
            if self.is_valid_position(next_pos):
                return direction

        return self.current_direction

    def collision_effect(self, collision_position):
        """
        Show collision effect on LED.

        Example:
            cp.collision_effect((3, 3))
        """
        x, y = collision_position
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        for color in colors:
            self.display[self.coord_to_index(x, y)] = color
            self.display.write()
            time.sleep(0.1)
            self.display[self.coord_to_index(x, y)] = (0, 0, 0)
            self.display.write()
            time.sleep(0.1)

    def twinkle_star(self, position, max_brightness=50, steps=10, delay=0.05):
        """
        Twinkle a star effect at a position.

        Example:
            cp.twinkle_star(10)
        """
        for brightness in range(1, max_brightness + 1, max_brightness // steps):
            self.display[position] = (brightness, brightness, brightness)
            self.display.write()
            time.sleep(delay)

        for brightness in range(max_brightness, 0, -max_brightness // steps):
            self.display[position] = (brightness, brightness, brightness)
            self.display.write()
            time.sleep(delay)

    def draw_clouds(self):
        """
        Draw clouds pattern.

        Example:
            cp.draw_clouds()
        """
        for i in range(8):
            self.display[i] = self.cloud_color
        for i in range(8, 16):
            self.display[i] = self.cloud_color
        self.display.write()

    def animate_rain(self, duration, delay, stop_new_drops=False):
        """
        Animate rain drops.

        :param duration: seconds to animate
        :param delay: delay between frames
        :param stop_new_drops: stop adding new drops if True

        Example:
            cp.animate_rain(5, 0.1)
        """
        rain_positions = []
        start_time = time.time()
        while time.time() - start_time < duration or rain_positions:
            if not stop_new_drops and time.time() - start_time < duration:
                start_position = random.choice(range(8, 16))
                rain_positions.append(start_position)
            for i in range(len(rain_positions)):
                if rain_positions[i] < 56:
                    self.display[rain_positions[i]] = (0, 0, 0)
                    rain_positions[i] += 8
                    self.display[rain_positions[i]] = self.rain_color
                else:
                    self.display[rain_positions[i]] = (0, 0, 0)
                    rain_positions[i] = None
            rain_positions = [pos for pos in rain_positions if pos is not None]
            self.display.write()
            time.sleep(delay)

    def lightning_effect(self):
        """
        Animate lightning flashes.

        Example:
            cp.lightning_effect()
        """
        for _ in range(3):
            for i in range(self.total_leds):
                self.display[i] = self.lightning_color
            self.display.write()
            time.sleep(0.05)
            self.clear_display()
            self.draw_clouds()
            self.display.write()
            time.sleep(0.05)

    def fade_out_rain(self, duration, steps=20):
        """
        Fade out rain animation.

        Example:
            cp.fade_out_rain(2, steps=20)
        """
        rain_positions = []
        fade_step_delay = duration / steps
        for step in range(steps, 0, -1):
            brightness = step / steps
            start_position = random.choice(range(8, 16))
            rain_positions.append(start_position)
            for i in range(len(rain_positions)):
                if rain_positions[i] < 56:
                    self.display[rain_positions[i]] = (0, 0, 0)
                    rain_positions[i] += 8
                    self.display[rain_positions[i]] = (
                        int(self.rain_color[0] * brightness),
                        int(self.rain_color[1] * brightness),
                        int(self.rain_color[2] * brightness)
                    )
                else:
                    self.display[rain_positions[i]] = (0, 0, 0)
                    rain_positions[i] = None
            rain_positions = [pos for pos in rain_positions if pos is not None]
            self.display.write()
            time.sleep(fade_step_delay)

    def fade_in_rainbow(self, duration):
        """
        Fade in rainbow colors.

        Example:
            cp.fade_in_rainbow(5)
        """
        rainbow_colors = [(35, 0, 0), (35, 18, 0), (35, 35, 0), (0, 35, 0),
                          (0, 0, 35), (12, 0, 35), (20, 0, 35)]
        steps = 20
        step_duration = duration / steps
        for step in range(1, steps + 1):
            brightness = step / steps
            for i in range(self.total_leds):
                color = rainbow_colors[i % len(rainbow_colors)]
                self.display[i] = (int(color[0] * brightness),
                                   int(color[1] * brightness),
                                   int(color[2] * brightness))
            self.display.write()
            time.sleep(step_duration)

    def fade_out_rainbow(self, duration):
        """
        Fade out rainbow colors.

        Example:
            cp.fade_out_rainbow(5)
        """
        rainbow_colors = [(35, 0, 0), (35, 18, 0), (35, 35, 0), (0, 35, 0),
                          (0, 0, 35), (12, 0, 35), (20, 0, 35)]
        steps = 20
        step_duration = duration / steps
        for step in range(steps, 0, -1):
            brightness = step / steps
            for i in range(self.total_leds):
                color = rainbow_colors[i % len(rainbow_colors)]
                self.display[i] = (int(color[0] * brightness),
                                   int(color[1] * brightness),
                                   int(color[2] * brightness))
            self.display.write()
            time.sleep(step_duration)

    def play_game(self):
        """
        Run the snake game.

        Example:
            cp.play_game()
        """
        self.reset_game()
        while True:
            self.update_snake_display()
            direction = self.get_direction_towards_food()
            head_x, head_y = self.snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])

            if not self.is_valid_position(new_head):
                self.collision_effect(new_head)
                break

            self.snake.insert(0, new_head)
            if new_head == self.food:
                self.food = self.spawn_food()
            else:
                self.snake.pop()

            time.sleep(0.2)

    def animate(self):
        """
        Run animation sequence.

        Example:
            cp.animate()
        """
        self.scroll_text("WELCOME TO CARES")
        self.clear_display()
        self.draw_clouds()
        time.sleep(2)
        self.animate_rain(duration=5, delay=0.1)
        self.lightning_effect()
        self.fade_out_rain(duration=2, steps=20)
        self.twinkle_star(35, max_brightness=50, steps=10, delay=0.05)
        self.fade_in_rainbow(duration=5)
        self.fade_out_rainbow(duration=5)

    def clearimage(self):
        """
        Clear all pixels.

        Example:
            cp.clearimage()
        """
        for i in range(self.total_leds):
            self.display[i] = (0, 0, 0)
        self.display.write()

    def smile(self):
        """
        Display smile face.

        Example:
            cp.smile()
        """
        self.clearimage()
        smile_coords = [
            16, 24, 32, 40, 9, 2, 3, 4, 5, 14, 23, 31, 39, 47, 54,
            61, 60, 59, 58, 49, 18, 21, 34, 43, 44, 37
        ]
        for i in smile_coords:
            self.display[i] = (0, 150, 0)
        self.display.write()

    def sad(self):
        """
        Display sad face.

        Example:
            cp.sad()
        """
        self.clearimage()
        sad_coords = [
            16, 24, 32, 40, 9, 2, 3, 4, 5, 14, 23, 31, 39, 47, 54,
            61, 60, 59, 58, 49, 18, 21, 42, 45, 35, 36,
        ]
        for i in sad_coords:
            self.display[i] = (120, 120, 0)
        self.display.write()

    def cry(self):
        """
        Display cry face.

        Example:
            cp.cry()
        """
        self.clearimage()
        cry_coords = [
            16, 24, 32, 40, 9, 2, 3, 4, 5, 14, 23, 31, 39, 47, 54,
            61, 60, 59, 58, 49, 18, 21, 42, 43, 44, 45,
        ]
        for i in cry_coords:
            self.display[i] = (150, 0, 0)
        self.display.write()

    def surprised(self):
        """
        Display surprised face.

        Example:
            cp.surprised()
        """
        self.clearimage()
        surprised_coords = [
            16, 24, 32, 40, 9, 2, 3, 4, 5, 14, 23, 31, 39, 47, 54,
            61, 60, 59, 58, 49, 18, 21, 42, 43, 44, 45, 35, 36
        ]
        for i in surprised_coords:
            self.display[i] = (160, 40, 240)
        self.display.write()

    def Demo(self):
        """
        Run demo animation and faces.

        Example:
            cp.Demo()
        """
        self.animate()
        self.play_game()
        self.cry()
        time.sleep(2)
        self.surprised()
        time.sleep(2)
        self.smile()
        time.sleep(2)
        self.sad()
        time.sleep(2)
        self.clearimage()

    
    class PixelSetter:
        """Helper class to set individual NeoPixel colors safely."""

        def __init__(self, neopixel_obj, total_leds):
            """
            Initialize PixelSetter helper.

            :param neopixel_obj: neopixel.NeoPixel instance
            :param total_leds: Number of LEDs in the matrix
            """
            self.np = neopixel_obj
            self.total_leds = total_leds

        def __getitem__(self, pixel):
            """
            Return a function that sets the color of the pixel at the given index.

            :param pixel: Integer index of pixel
            :return: Function(r, g, b) to set color

            Example:
            ```python
            setter = cp.PixelSetter(cp.display, cp.total_leds)
            set_pixel_5 = setter[5]
            set_pixel_5(255, 0, 0)  # Set pixel 5 to red
            ```
            """
            if not isinstance(pixel, int):
                raise TypeError(f"Pixel index must be an integer, got {type(pixel).__name__}")
            if not (0 <= pixel < self.total_leds):
                raise IndexError(f"Invalid index {pixel}. Must be 0 <= pixel < {self.total_leds}")

            def set_pixel_color(r, g, b):
                for val, name in zip((r, g, b), "RGB"):
                    if not isinstance(val, (int, float)):
                        raise TypeError(f"{name} value must be a number, got {type(val).__name__}")
                    if not (0 <= val <= 255):
                        raise ValueError(f"{name} value {val} is out of range (0–255).")

                # Dim colors by factor 0.1 for brightness control
                r_ = int(r * 0.1)
                g_ = int(g * 0.1)
                b_ = int(b * 0.1)

                self.np[pixel] = (r_, g_, b_)
                self.np.write()

            return set_pixel_color

    @property
    def setPixel(self):
        """
        Accessor property to get PixelSetter instance.

        Example:
        ```python
        cp = CARESpixel(pin=5, total_leds=64)
        cp.setPixel[3](255, 0, 0)  # Set pixel 3 to red (dimmed)
        ```
        """
        return self.PixelSetter(self.display, self.total_leds)

    def matrixColor(self, r, g, b):
        """
        Set all pixels to the specified RGB color (dimmed).

        :param r: Red (0–255)
        :param g: Green (0–255)
        :param b: Blue (0–255)

        Example:
        ```python
        cp.matrixColor(10, 0, 0)  # Set all pixels dim red
        ```
        """
        for val, name in zip((r, g, b), "RGB"):
            if not isinstance(val, (int, float)):
                raise TypeError(f"{name} value must be a number, got {type(val).__name__}")
            if not (0 <= val <= 255):
                raise ValueError(f"{name} value {val} is out of range (0–255).")

        r_ = int(r * 0.1)
        g_ = int(g * 0.1)
        b_ = int(b * 0.1)

        for npixel in range(self.total_leds):
            self.display[npixel] = (r_, g_, b_)
        self.display.write()

    def clearAll(self):
        """
        Turn off all pixels in the matrix.

        Example:
        ```python
        cp.clearAll()
        ```
        """
        for npixel in range(self.total_leds):
            self.display[npixel] = (0, 0, 0)
        self.display.write()
        print("All pixels cleared.")
        
class Servo:
    def __init__(self, pin, freq=50):
        """
        Initialize a servo motor.

        :param pin: A Pin object (your custom Pin class) or machine.Pin instance.
        :param freq: PWM frequency in Hz (default 50).

        Example:
        ```python
        servo5 = Servo(Pin(5))          # Using your custom Pin class
        servo15 = Servo(machine.Pin(15))  # Using machine.Pin directly
        ```
        """
        if isinstance(pin, Pin):
            self.pwm = machine.PWM(pin.pin, freq=freq)
        elif isinstance(pin, machine.Pin):
            self.pwm = machine.PWM(pin, freq=freq)
        else:
            raise ValueError("Pin must be a Pin or machine.Pin object.")
        
        self.min_duty = 40  # Duty cycle for 0 degrees
        self.max_duty = 115  # Duty cycle for 180 degrees

    def write_angle(self, angle):
        """
        Set the servo angle between 0 and 180 degrees.

        :param angle: Integer angle (0 to 180).

        Example:
        ```python
        servo5 = Servo(Pin(5))
        servo5.write_angle(90)  # Move servo to 90 degrees
        servo5.write_angle(0)   # Move servo to 0 degrees
        ```
        """
        if 0 <= angle <= 180:
            duty = self.min_duty + (self.max_duty - self.min_duty) * angle // 180
            self.pwm.duty(duty)
        else:
            raise ValueError("Angle must be between 0 and 180 degrees.")


        
class Pin:
    IN = machine.Pin.IN  # Alias for input mode
    OUT = machine.Pin.OUT  # Alias for output mode

    def __init__(self, pin_number, mode=machine.Pin.OUT):
        """
        Initialize a pin for digital or analog operations.

        Args:
            pin_number (int): The pin number.
            mode (int): Use `Pin.IN` or `Pin.OUT` for input or output mode.

        Example:
        ```python
        pin_in = Pin(12, Pin.IN)   # Initialize pin 12 as input
        pin_out = Pin(14, Pin.OUT) # Initialize pin 14 as output
        ```
        """
        if mode not in [machine.Pin.IN, machine.Pin.OUT]:
            raise ValueError("Invalid mode. Use Pin.IN or Pin.OUT.")

        self.pin = machine.Pin(pin_number, mode)
        self.mode = mode
        self.is_analog = False  # Track if analog functionality is used
        self.adc = None  # For analog input
        self.pwm = None  # For analog output

    def analogRead(self):
        """
        Read analog value (0-4095) if pin is input with ADC.

        Returns:
            int: ADC reading value.

        Example:
        ```python
        pin = Pin(34, Pin.IN)
        value = pin.analogRead()
        print("ADC value:", value)
        ```
        """
        if self.mode != machine.Pin.IN:
            raise AttributeError("analogRead is only supported in input mode.")
        if not self.is_analog:
            self.adc = machine.ADC(self.pin)
            self.adc.atten(machine.ADC.ATTN_11DB)  # Configure attenuation
            self.is_analog = True
        return self.adc.read()

    def analogReadVoltage(self, reference_voltage=3.3):
        """
        Convert ADC reading to voltage.

        Args:
            reference_voltage (float): Reference voltage, default is 3.3V.

        Returns:
            float: Voltage value.

        Example:
        ```python
        pin = Pin(34, Pin.IN)
        voltage = pin.analogReadVoltage()
        print("Voltage:", voltage)
        ```
        """
        if not self.is_analog or self.mode != machine.Pin.IN:
            raise AttributeError("analogReadVoltage is only supported in input mode.")
        adc_value = self.analogRead()
        return adc_value * (reference_voltage / 4095)

    def analogWrite(self, value):
        """
        Write PWM duty cycle to pin (0-255) if configured as output.

        Args:
            value (int): PWM duty cycle between 0 and 255.

        Example:
        ```python
        pin = Pin(14, Pin.OUT)
        pin.analogWrite(128)  # Set PWM to about 50% duty cycle
        ```
        """
        if self.mode != Pin.OUT:
            raise AttributeError("analogWrite is only supported in output mode.")
        if self.pwm is None:
            self.pwm = machine.PWM(self.pin, freq=1000)  # PWM freq 1kHz
        if 0 <= value <= 255:
            self.pwm.duty(value * 4)  # Scale 0-255 to 0-1023 duty
        else:
            raise ValueError("Value must be in the range 0-255.")

    def digitalRead(self):
        """
        Read digital value (0 or 1) if pin is input.

        Returns:
            int: Digital pin value (0 or 1).

        Example:
        ```python
        pin = Pin(12, Pin.IN)
        val = pin.digitalRead()
        print("Digital value:", val)
        ```
        """
        if self.mode != Pin.IN:
            raise AttributeError("digitalRead is only supported in input mode.")
        return self.pin.value()

    def digitalWrite(self, value):
        """
        Write digital value (0 or 1) if pin is output.

        Args:
            value (int): 0 or 1 to set pin low or high.

        Example:
        ```python
        pin = Pin(14, Pin.OUT)
        pin.digitalWrite(1)  # Set pin high
        pin.digitalWrite(0)  # Set pin low
        ```
        """
        if self.mode != Pin.OUT:
            raise AttributeError("digitalWrite is only supported in output mode.")
        if value not in (0, 1):
            raise ValueError(f"digitalWrite only accepts 0 or 1, got {value}")

        self.pin.value(value)

# # Define __all__ for imports
# __all__ = ['Pin', 'CARESpixel']
# 

class sevenSegment:
    DIGIT_TO_SEGMENT = {
        '0': 0b00111111,
        '1': 0b00000110,
        '2': 0b01011011,
        '3': 0b01001111,
        '4': 0b01100110,
        '5': 0b01101101,
        '6': 0b01111101,
        '7': 0b00000111,
        '8': 0b01111111,
        '9': 0b01101111,
        'A': 0b01110111,
        'C': 0b00111001,
        'E': 0b01111001,
        'F': 0b01110001,
        'H': 0b01110110,
        'J': 0b00001110,
        'L': 0b00111000,
        'O': 0b00111111,
        'P': 0b01110011,
        'S': 0b01101101,
        'U': 0b00111110,
        '-': 0b01000000,
        ' ': 0b00000000,
        '^': 0b01100011,
    }

    def __init__(self, clkPin=22, dioPin=21, bitDelay=100):
        """
        Initialize the sevenSegment display.

        :param clkPin: Clock pin number (default 22).
        :param dioPin: Data pin number (default 21).
        :param bitDelay: Delay in microseconds for communication (default 100).

        Example:
        ```python
        segment = sevenSegment(clkPin=5, dioPin=4)
        OR
        segment = sevenSegment()

        ```
        """
        self.clk = Pin(clkPin, Pin.OUT)
        self.dio = Pin(dioPin, Pin.OUT)
        self.bitDelay = bitDelay
        self.clk.digitalWrite(1)
        self.dio.digitalWrite(1)

    def writeByte(self, data):
        """
        Send a byte to the display.

        :param data: Byte data to send.

        Example:
        ```python
        segment.writeByte(0xFF)
        ```
        """
        for _ in range(8):
            self.clk.digitalWrite(0)
            self.dio.digitalWrite(data & 0x01)
            self.clk.digitalWrite(1)
            data >>= 1
        self.clk.digitalWrite(0)
        self.dio.digitalWrite(1)
        self.clk.digitalWrite(1)

    def setSegments(self, segments, colon=False, brightness=7):
        """
        Set the segments on the display.

        :param segments: List of 4 bytes, each representing segments for a digit.
        :param colon: Boolean, True to turn colon on.
        :param brightness: Brightness level (0 to 7).

        Example:
        ```python
        segments = [0x3F, 0x06, 0x5B, 0x4F]  # Displays "0123"
        segment.setSegments(segments, colon=True, brightness=5)
        ```
        """
        self.start()
        self.writeByte(0x40)
        self.stop()

        self.start()
        self.writeByte(0xC0)
        for i in range(4):
            byte = segments[i]
            if colon and i == 1:
                byte |= 0b10000000
            self.writeByte(byte)
        self.stop()

        self.start()
        self.writeByte(0x88 | (brightness & 0x07))
        self.stop()

    def encodeCharacter(self, char):
        """
        Encode a character to its 7-segment byte representation.

        :param char: Character to encode.
        :return: Byte representing the segments.

        Example:
        ```python
        byte_val = segment.encodeCharacter('A')
        print(bin(byte_val))
        ```
        """
        return self.DIGIT_TO_SEGMENT.get(char.upper(), 0)

    def displayDigit(self, inputValue, brightness=7):
        """
        Display a number or string on the 4-digit 7-segment display.

        :param inputValue: int or str (max 4 digits/characters).
        :param brightness: Brightness level (0 to 7).

        Example:
        ```python
        segment.displayDigit(1234)
        segment.displayDigit("AbCd")
        ```
        """
        segments = [0] * 4

        if isinstance(inputValue, int):
            isNegative = inputValue < 0
            inputValue = abs(inputValue)

            if inputValue >= 10**4:
                raise ValueError("Overflow: Input exceeds 4 digits.")

            for i in range(3, -1, -1):
                segments[i] = self.encodeCharacter(str(inputValue % 10))
                inputValue //= 10

            if isNegative:
                segments[0] = 0b01000000  # Negative sign
        elif isinstance(inputValue, str):
            if len(inputValue) > 4:
                raise ValueError("Overflow: String input exceeds 4 characters.")
            for i, char in enumerate(inputValue[:4]):
                segments[i] = self.encodeCharacter(char)

        self.setSegments(segments, colon=False, brightness=brightness)

    def displayColon(self, state, brightness=7):
        """
        Turn the colon on or off.

        :param state: 1 to turn colon on, 0 to turn off.
        :param brightness: Brightness level (0 to 7).

        Example:
        ```python
        segment.displayColon(1)  # Turn colon on
        segment.displayColon(0)  # Turn colon off
        ```
        """
        self.setSegments([0, 0, 0, 0], colon=(state == 1), brightness=brightness)

    def start(self):
        """Start communication with the display."""
        self.dio.digitalWrite(1)
        self.clk.digitalWrite(1)
        self.dio.digitalWrite(0)
        self.clk.digitalWrite(0)

    def stop(self):
        """Stop communication with the display."""
        self.clk.digitalWrite(0)
        self.dio.digitalWrite(0)
        self.clk.digitalWrite(1)
        self.dio.digitalWrite(1)

    def write_digit(self, inputValue, brightness=7):
        """
        Display digit(s) using displayDigit.

        :param inputValue: int or str.
        :param brightness: Brightness level.

        Example:
        ```python
        segment.write_digit(5678)
        ```
        """
        self.displayDigit(inputValue, brightness=brightness)

    def write_colon(self, state, brightness=7):
        """
        Control colon display.

        :param state: 1 to turn colon on, 0 to turn off.
        :param brightness: Brightness level.

        Example:
        ```python
        segment.write_colon(1)
        ```
        """
        self.displayColon(state, brightness=brightness)

  
__all__ = ['Pin', 'CARESpixel','sevenSegment','Servo', 'OLED' ]



