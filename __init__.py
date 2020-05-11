from mycroft import MycroftSkill, intent_file_handler


class LedRing(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('ring.led.intent')
    def handle_ring_led(self, message):
        self.speak_dialog('ring.led')


def create_skill():
    return LedRing()

