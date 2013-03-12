from psycorax import generators
import time
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

    def resize(self, server_details):
        f_l = self.nova.flavor_list()['nova_resp']['flavors']
        server_id = server_details['id']
        orig_flavor = server_details['flavor']['id']
        size_choice = random.choice(f_l)
        size = size_choice['id']

        # If I randomly picked the same size the server is, pick another
        if size == orig_flavor:
            for flv in f_l:
                if flv['id'] == size:
                    index = f_l.index(flv)
                    f_l.pop(index)
                    size_choice = random.choice(f_l)
                    size = size_choice['id']
        # Resize the instance
        self.nova.re_sizer(server_id, size)

        # Wait for the instance to finish the resize
        for retry in generators.retryloop(attempts=200,
                                          delay=15,
                                          timeout=960):
            time.sleep(15)
            server = self.nova.server_info(server_id)['nova_resp']
            status = server['server']['status'].upper()
            if status == ('ACTIVE' or 'ERROR'):
                server_id = server['server']['id']
                self.nova.server_nuker(server_id)
            elif not status == 'VERIFY_RESIZE':
                try:
                    retry()
                except Exception:
                    self.nova.server_nuker(server_id)
        if status == 'VERIFY_RESIZE':
            tof = [True, False]
            action = random.choice(tof)
            crs = self.nova.confirm_revert_resize(server_id=server_id,
                                                  confirm=action)
            if tof:
                if crs['nova_status'] <= 300:
                    self.nova.server_nuker(server_id)
                else:
                    self.nova.server_nuker(server_id)
        else:
            self.nova.server_nuker(server_id)
