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


Simple Use
~~~~~~~~~~


.. code-block:: bash 

    psycorax -u usename -a apikey --os-rax-auth dfw --start


Notes
-----

* If you give psycorax an SSH key with the `--ssh-key` flag, it will attempt to login to the instances and cause additional chaos. 
* If you specify the number of instances that you would like to test with the `--attack-cc` psycorax will attempt to test a random set of instances between 1 and the number you set.