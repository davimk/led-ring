from mycroft import MycroftSkill
import zmq # Asynchronous messaging framework for Matrix Voice
from matrix_io.proto.malos.v1 import driver_pb2 # MATRIX Protocol Buffer driver library
from matrix_io.proto.malos.v1 import io_pb2 # MATRIX Protocol Buffer sensor library

LED_COUNT = 18 # Number of LEDs on Matrix Voice
MATRIX_IP = '127.0.0.1' # Local Matrix Voice device ip
EVERLOOP_PORT = 20021 # Matrix Voice Driver Base port
# Turn on all LEDs
ON = {
        0:{"blue":50, "red":0, "green":0, "white":0},
        1:{"blue":50, "red":0, "green":0, "white":0},
        2:{"blue":50, "red":0, "green":0, "white":0},
        3:{"blue":50, "red":0, "green":0, "white":0},
        4:{"blue":50, "red":0, "green":0, "white":0},
        5:{"blue":50, "red":0, "green":0, "white":0},
        6:{"blue":50, "red":0, "green":0, "white":0},
        7:{"blue":50, "red":0, "green":0, "white":0},
        8:{"blue":50, "red":0, "green":0, "white":0},
        9:{"blue":50, "red":0, "green":0, "white":0},
        10:{"blue":50, "red":0, "green":0, "white":0},
        11:{"blue":50, "red":0, "green":0, "white":0},
        12:{"blue":50, "red":0, "green":0, "white":0},
        13:{"blue":50, "red":0, "green":0, "white":0},
        14:{"blue":50, "red":0, "green":0, "white":0},
        15:{"blue":50, "red":0, "green":0, "white":0},
        16:{"blue":50, "red":0, "green":0, "white":0},
        17:{"blue":50, "red":0, "green":0, "white":0}
        }
# Turn off all LEDs
OFF = {}
# Turn on two arcs of blue LEDs while processing an utterance.
THINK = {
            17:{"blue":50, "red":0, "green":0, "white":0},
            0:{"blue":50, "red":0, "green":0, "white":0},
            1:{"blue":50, "red":0, "green":0, "white":0},
            8:{"blue":50, "red":0, "green":0, "white":0},
            9:{"blue":50, "red":0, "green":0, "white":0},
            10:{"blue":50, "red":0, "green":0, "white":0}
            }
# Turn on two arcs of blue LEDs, 90 degrees from think arc, while speaking.
SPEAK = {
            3:{"blue":50, "red":0, "green":0, "white":0},
            4:{"blue":50, "red":0, "green":0, "white":0},
            5:{"blue":50, "red":0, "green":0, "white":0},
            13:{"blue":50, "red":0, "green":0, "white":0},
            14:{"blue":50, "red":0, "green":0, "white":0},
            15:{"blue":50, "red":0, "green":0, "white":0}
            }
"""
Make an image for Matrix Voice Everloop LED driver.
Arguments:
ledCount - total number of Everloop ring LEDs
ledOn - Dictionary containing integer key of which LED to turn on (0-17).
        Value is another dictionary containing brightness key of blue, red, green, and white
        with integer value (0-255).
Returns an image that can be sent to the Everloop driver port.
"""
def ring_image(led_count, ledOn):
    # Create a new driver config
    driver_config_proto = driver_pb2.DriverConfig()
    # Create an empty Everloop image
    image = []
    # Set individual LED value
    for led in range(led_count):
        if led in ledOn:
            ledValue = io_pb2.LedValue() # Protocol buffer custom type for Matrix Voice
            ledValue.blue = ledOn[led]["blue"]
            ledValue.red = ledOn[led]["red"]
            ledValue.green = ledOn[led]["green"]
            ledValue.white = ledOn[led]["white"]
            image.append(ledValue)
        else:
            ledValue = io_pb2.LedValue()
            ledValue.blue = 0
            ledValue.red = 0
            ledValue.green = 0
            ledValue.white = 0
            image.append(ledValue)
    # Store the Everloop image in driver configuration
    driver_config_proto.image.led.extend(image)
    return driver_config_proto.SerializeToString()
"""
Listen for messages and control Everloop LEDs in response.
"""
class LedRing(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        # Define zmq socket
        self.context = zmq.Context()
        # Create a Pusher socket
        self.socket = self.context.socket(zmq.PUSH)
        # Connect Pusher to configuration socket
        self.socket.connect('tcp://{0}:{1}'.format(MATRIX_IP, EVERLOOP_PORT))

    def initialize(self):
        self.add_event('recognizer_loop:wakeword',
                       self.handler_wakeword)
        self.add_event('recognizer_loop:record_end',
                       self.handler_record_end)
        self.add_event('recognizer_loop:utterance',
                       self.handler_utterance)
        self.add_event('recognizer_loop:audio_output_start',
                       self.handler_audio_output_start)
        self.add_event('recognizer_loop:audio_output_end',
                       self.handler_audio_output_end)
        self.add_event('mycroft.stop',
                        self.handler_mycroft_stop)
        self.add_event('mycroft.audio.service.resume',
                        self.handler_mycroft_audio_service_resume)
        # Make Everloop images.
        self.ring_on = ring_image(LED_COUNT, ON)
        self.ring_off = ring_image(LED_COUNT, OFF)
        self.ring_think = ring_image(LED_COUNT, THINK)
        self.ring_speak = ring_image(LED_COUNT, SPEAK)

    def handler_wakeword(self, message):
        # Send Everloop image to Everloop driver port through ZMQ socket.
        self.socket.send(self.ring_on)

    def handler_record_end(self, message):
        self.socket.send(self.ring_off)

    def handler_utterance(self, message):
        self.socket.send(self.ring_think)

    def handler_audio_output_start(self, message):
        self.socket.send(self.ring_speak)

    def handler_audio_output_end(self, message):
        self.socket.send(self.ring_off)

    def handler_mycroft_stop(self, message):
        self.socket.send(self.ring_off)

    def handler_mycroft_audio_service_resume(self, message):
        self.socket.send(self.ring_off)

    # Clean up ZMQ socket and context on shutdown.
    def shutdown(self):
        self.socket.close()
        self.context.term
        self.log.debug("The ZMQ socket and context have been closed.")

def create_skill():
    return LedRing()
