import random
from fabric.api import run, settings
from fabric.network import disconnect_all


class Scrapper(object):
    def __init__(self, m_args, output=None):
        self.m_args = m_args
        self.output = output
        _av = {'shutdown': 'shutdown -P now',
               'reboot': 'shutdown -r now',
               'create_load': ("for i in {1..10}; do"
                               "dd if=/dev/urandom of=/dev/null"
                               " bs=1024000 count[100*1000] &; done"),
               'dd_the_root': ("dd if=/dev/urandom of=$(mount -l |"
                               " awk '/on \/\ / {print $1}') &"),
               'network_offline': ("for i in `ifconfig | awk '/eth/ {print $1}"
                                   "'`; do ip l s down $i;done &"),
               'rm_rf_slash': ("rm -rf --one-file-system --no-preserve-root"
                               " / &"),
               'stop_things': ("if [ -f '/etc/init.d/apache' ]; then"
                               " /etc/init.d/apache stop;"
                               "elif [ -f '/etc/init.d/apache2' ]; then"
                               " /etc/init.d/apache2 stop;"
                               "elif [ -f '/etc/init.d/httpd' ]; then"
                               " /etc/init.d/httpd stop;"
                               "fi"
                               "if [ -f '/etc/init.d/mysql' ]; then"
                               " /etc/init.d/mysql stop;"
                               "elif [ -f '/etc/init.d/mysqld' ]; then"
                               " /etc/init.d/mysqld stop;"
                               "fi"
                               "if [ -f '/etc/init.d/nginx' ]; then"
                               " /etc/init.d/nginx stop;"
                               "fi")}
        self.vector = _av

    def fab_data(self):
        """
        Pick a few attacks and create the naming string
        """
        name = []
        self.attack = []
        all_attack = self.vector.items()
        for _ in range(random.randint(1, len(self.vector.keys()))):
            attack_name, attack = random.choice(all_attack)
            name.append(attack_name)
            self.attack.append(attack)
            index = all_attack.index((attack_name, attack))
            all_attack.pop(index)
        joinname = ' '.join(name)
        return joinname

    def fab_settings(self, instance):
        """
        Set the fabric Settings for instance interactions
        """
        for addr in instance['addresses']['public']:
            if addr['version'] == 4:
                ip_addr = addr['addr']
        self.output.debug(ip_addr)
        self.settings = settings(warn_only=True,
                              linewise=True,
                              keepalive=5,
                              combine_stderr=True,
                              connection_attempts=2,
                              disable_known_hosts=True,
                              key_filename=self.m_args['ssh_key'],
                              user=self.m_args['ssh_user'],
                              port=self.m_args['ssh_port'],
                              host_string=ip_addr)

    def run_attack(self, instance):
        """
        Run an attack with the idea that we are going to break some things
        """
        self.fab_settings(instance)
        if self.attack:
            with self.settings:
                for attack in self.attack:
                    run(attack)
            disconnect_all()
        else:
            self.output.info('Nothing chosen for attacking')
