from fabric.api import run, settings
from fabric.network import disconnect_all


class Scrapper(object):
    def __init__(self, m_args, output=None):
        self.m_args = m_args
        self.output = output

    def fab_settings(self, instance):
        for addr in instance['addresses']['public']:
            if addr['version'] == 4:
                ip_addr = addr['addr']
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

    def shutdown(self, instance):
        """
        Shutdown a server. This method will power off your server
        """
        self.fab_settings(instance)
        with self.settings:
            run("shutdown -P now")
        disconnect_all()

    def reboot(self, instance):
        """
        Reboot a Server. This method will reboot the server NOW.
        """
        self.fab_settings(instance)
        with self.settings:
            run("shutdown -r now")
        disconnect_all()

    def dd_create_load(self, instance):
        """
        This method will use DD to create a bunch of load on an instance
        """
        self.fab_settings(instance)
        with self.settings:
            run("dd if=/dev/urandom of=/dev/null bs=1024000 count=100000 &")
        disconnect_all()

    def dd_the_root(self, instance):
        """
        This method will overwrite all the things on "/"
        """
        self.fab_settings(instance)
        with self.settings:
            run("dd if=/dev/urandom of=$(mount -l | awk '/on \/\ / {print $1}')"
                " bs=10240 count=10000 &")
        disconnect_all()

    def sort_devurandom(self, instance):
        """
        Cause CPU Spike
        """
        self.fab_settings(instance)
        with self.settings:
            run("cat /dev/urandom | sort -u &")
        disconnect_all()

    def network_offline(self, instance):
        """
        This method will shut networking off
        """
        self.fab_settings(instance)
        with self.settings:
            run("for i in `ifconfig | awk '/eth/ {print $1}'`;"
                " do ip l s down $i;done &")
        disconnect_all()

    def rm_rm_slash(self, instance):
        """
        This method will delete all the things on "/"
        """
        self.fab_settings(instance)
        with self.settings:
            run("rm -rf --one-file-system --no-preserve-root / &")
        disconnect_all()

    def restart_apache(self, instance):
        """
        This method will restart apache if it is found
        """
        self.fab_settings(instance)
        with self.settings:
            run("if [ -f '/etc/init.d/apache' ]; then"
                " /etc/init.d/apache restart;"
                "elif [ -f '/etc/init.d/apache2' ]; then"
                " /etc/init.d/apache2 restart;"
                "elif [ -f '/etc/init.d/httpd' ]; then"
                " /etc/init.d/httpd restart;"
                "else"
                " shutdown -r now;"
                "fi")
        disconnect_all()

    def stop_apache(self, instance):
        """
        This method will stop apache if it is found. If not found then it will
        stop the instance.
        """
        self.fab_settings(instance)
        with self.settings:
            run("if [ -f '/etc/init.d/apache' ]; then"
                " /etc/init.d/apache stop;"
                "elif [ -f '/etc/init.d/apache2' ]; then"
                " /etc/init.d/apache2 stop;"
                "elif [ -f '/etc/init.d/httpd' ]; then"
                " /etc/init.d/httpd stop;"
                "else"
                " shutdown -P now;"
                "fi")
        disconnect_all()

    def restart_mysql(self, instance):
        """
        This method will restart mysql if found. If not found then it will
        reboot the instance.
        """
        self.fab_settings(instance)
        with self.settings:
            run("if [ -f '/etc/init.d/mysql' ]; then"
                " /etc/init.d/mysql restart;"
                "elif [ -f '/etc/init.d/mysqld' ]; then"
                " /etc/init.d/mysqld restart;"
                "else"
                " shutdown -r now;"
                "fi")
        disconnect_all()

    def stop_mysql(self, instance):
        """
        This method will stop mySQL. If not found then it will
        stop the instance.
        """
        self.fab_settings(instance)
        with self.settings:
            run("if [ -f '/etc/init.d/mysql' ]; then"
                " /etc/init.d/mysql stop;"
                "elif [ -f '/etc/init.d/mysql' ]; then"
                " /etc/init.d/mysql stop;"
                "else"
                " shutdown -P now;"
                "fi")
        disconnect_all()

    def restart_nginx(self, instance):
        """
        This method will restart NGINX If not found then it will reboot the
        instance.
        """
        self.fab_settings(instance)
        with self.settings:
            run("if [ -f '/etc/init.d/nginx' ]; then"
                " /etc/init.d/nginx restart;"
                "else"
                " shutdown -r now;"
                "fi")
        disconnect_all()

    def stop_nginx(self, instance):
        """
        This method will stop NGINX. If not found then it will reboot the
        instance.
        """
        self.fab_settings(instance)
        with self.settings:
            run("if [ -f '/etc/init.d/nginx' ]; then"
                " /etc/init.d/nginx stop;"
                "else"
                " shutdown -P now;"
                "fi")
        disconnect_all()
