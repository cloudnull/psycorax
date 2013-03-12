PsycoRAX
########
:date: 2013-03-05 00:00
:tags: Monitoring, Administration, Automation, Stress Testing
:Authors: Kevin Carter

Psyco Rax is an environment stress testing system that will cause havoc
=======================================================================

When building a cloudy environment, testing is required in order to ensure your application and services remain online and are redundant.

The PsycoRAX system will automate random stress testing on instances from within the an Openstack Cloud. 


Overview
--------

PsycoRax is random, and unpredictable but manageable :
    The PsycoRax system runs as a python based Full UNIX daemon conforming to PEP4134. The application will pull instances from the Openstack Servers list, validate they are in an "ACTIVE" state and then ensure they are tagged as being available for testing. The tag system employed is a simple Metadata tag *"ameba_managed"* which is added to an instance. If the system detects the TAG it will then ensure that the instance has no Pending task state.


Nothing is ever a set integer in PsycoRAX:
    All supplied integers will be used as a range. To explain, the time interval is a range in minutes which defaults to 60 minutes. If you specify the number of instances, to test with the `--attack-cc` flag, psycorax will attempt to test a random set of instances between 1 and the number you set. Additionally, the attack vector being used is also chosen at random from the available pool of vectors.


Check your Logs:
    While PsycoRAX is harmful to the environment, it does log everything. This allows for traceability. 



Simple Use
~~~~~~~~~~


.. code-block:: bash 

    psycorax -u $usename -a $apikey --os-rax-auth $dc --start


Functions of PsycoRax
~~~~~~~~~~~~~~~~~~~~~

API Functions:
    * nuke : Delete an Instance 
    * reboot : Reboots an Instance
    * resize : Resizes an instance to a random size, then either revert it or nuke it


Fabric Functions:
    * shutdown : From within the instance, it is shutoff
    * reboot : Issue reboot now from within an instance
    * dd_create_load : Use DD to create load on the box
    * dd_the_root : Use DD to corrupt the file system
    * sort_devurandom : Case Load by attempting to uniquely sort /dev/urandom
    * network_offline : Disable networking
    * rm_rm_slash : Delete Everything
    * restart_apache : Look for Apache, if found restart it, if not found restart the instance.
    * stop_apache : Look for Apache, if found stop it, if not found shut the instance down.
    * restart_mysql : Look for MySQL, if found restart it, if not found restart the instance.
    * stop_mysql : Look for MySQL, if found stop it, if not found shut the instance down.
    * restart_nginx : Look for NGINX, if found restart it, if not found restart the instance.
    * stop_nginx : Look for NGINX, if found stop it, if not found shut the instance down.


Notes
-----

* To use the Fabric Functions you must supply PsycoRAX with an SSH key by using the `--ssh-key` flag, it will attempt to login to the instances and cause additional chaos.