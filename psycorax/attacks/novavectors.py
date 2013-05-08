import random


class NovaAttacks(object):
    def __init__(self, nova):
        self.nova = nova

    def nuke(self, server_details):
        self.nova.server_nuker(server_details['id'])

    def reboot(self, server_details):
        tof = [True, False]
        action = random.choice(tof)
        self.nova.re_booter(server_details['id'], hard_reboot=action)
