from __future__ import print_function
import traceback
import random

# Import bookofnova
from bookofnova import authentication, computelib

# Local Imports
from psycorax import generators


class NotAuthenticated(Exception):
    pass


class NothingToMessWith(Exception):
    pass


class Crazyness(object):
    def __init__(self, m_args, output):
        """
        Prep the Crazy man to do things.  This requires an openstack set of
        Credentials to get started.
        """
        # Set Initial Arguments
        self.m_args = m_args

        # Set the Log Handler
        self.log = output

        # Prep Nova For Use
        self.nova = computelib.NovaCommands(m_args=self.m_args,
                                            output=self.log.info)

        # Authentication with Nova
        self.auth = authentication.Authentication(m_args=self.m_args,
                                                  output=self.log.info)

    def authenticate(self):
        """
        Authenticate against an OpenStack API if not 200 Raise an exception
        """
        try:
            self.m_args = self.auth.os_auth()
        except Exception:
            self.log.critical(self.m_args)

        if self.m_args['nova_status'] is 200:
            self.log.info('"%s" User Authenticated'
                          % self.m_args['nova_reason'])
        else:
            raise NotAuthenticated('Authentication Failure,'
                                   ' please check Credentials')

    def nodes_to_destruct(self):
        """
        Figure our the nodes that I can play with.  The node list with all
        details is created then the node list looks though the instances for
        metadata which is set as "ameba_managed" for the Key. If this metadata
        key is found the instance is loaded into our list of dictionaries
        and is ready for a good time. Note that the application will only load
        instances that have an "ACTIVE" state and are not in a Pending Task
        State.
        """
        load_inst = self.nova.server_list_detail()['nova_resp']
        self.log.debug(load_inst)
        attack_insts = []
        for inst in load_inst['servers']:
            if 'ameba_managed' in inst['metadata']:
                if inst['status'] == 'ACTIVE':
                    if "OS-EXT-STS:task_state" in inst:
                        if not inst['OS-EXT-STS:task_state']:
                            attack_insts.append(inst)
        self.log.info('Discovering Instances I can Play with')
        return attack_insts

    def destructivizer(self):
        """
        The things that I know I can play with.
        """
        import inspect
        from psycorax.attacks import novavectors, fabricvector
        psyco_path = {}
        novacomp = novavectors.NovaAttacks(self.nova)
        base_options = inspect.getmembers(novacomp, predicate=inspect.ismethod)
        for opt_b in base_options:
            opt = opt_b[0]
            if opt is not '__init__':
                psyco_path.update({'API_%s' % str(opt): opt_b[1]})

        if self.m_args['ssh_key']:
            fabs = fabricvector.Scrapper(self.m_args)
            options = inspect.getmembers(fabs, predicate=inspect.ismethod)
            for opt_s in options:
                opt = opt_s[0]
                if opt is not '__init__' or not 'fab_settings':
                    psyco_path.update({'FAB_%s' % str(opt): opt_s[1]})

            domer_style = {}
            psyco_path.update(domer_style)
        self.log.info('Packing my tool bag')
        return psyco_path

    def crazy_man(self):
        """
        Let the Crazy man loose in our environment.
        """
        nodes = self.nodes_to_destruct()
        try:
            if nodes:
                num_nodes = len(nodes)
                self.log.info('We discovered "%s" that will be played with'
                              % num_nodes)
            else:
                raise NothingToMessWith
        except NothingToMessWith:
            self.log.info('No Instaces were found to Play with.'
                          ' So Nothing to do...')

        attacks = self.destructivizer()
        # Set a list of all of the processes which we are working on
        attack_procs = []
        # pick our vic
        node_count = len(nodes)
        try:
            if node_count == 0:
                raise NothingToMessWith('Due to having a "%s" node count,'
                                        ' I have nothing to do.' % node_count)
            elif self.m_args['cc_attack'] <= 0:
                if node_count == 1:
                    num_nodes = 1
                else:
                    num_nodes = random.randrange(1, node_count)
            elif self.m_args['cc_attack'] == 1:
                num_nodes = 1
            else:
                if self.m_args['cc_attack'] > node_count:
                    self.m_args['cc_attack'] = node_count
                num_nodes = random.randrange(1, self.m_args['cc_attack'])
            # Attack what I know to attack
            self.domer(nodes, num_nodes, attacks, attack_procs)
        except NothingToMessWith:
            self.log.info('I have nothing to do at this time...')
        except ValueError:
            self.log.info('Error Deciding on Target Nodes.'
                          ' Values are : %s, %s' % (self.m_args['cc_attack'],
                                                    node_count))

    def domer(self, nodes, num_nodes, attacks, attack_procs):
        self.log.info('Picking "%s" Lucky Nodes' % num_nodes)
        lucky_ones = random.sample(nodes, num_nodes)
        # pick our method for pain
        try:
            vectors = []
            for node in lucky_ones:
                destructive = random.choice(attacks.keys())
                method = attacks[destructive]
                if self.m_args['os_verbose']:
                    self.log.info(self.m_args)
                    self.log.info(node)
                msg = ('Instance UUID => "%s"'
                       ' Attack vector ==> "%s"'
                       % (node['id'], destructive))
                self.log.warn(msg)
                task = (method, node)
                vectors.append(task)
                del task
            if not self.m_args['test']:
                generators.worker_proc(job_action=vectors)
            else:
                for job in vectors:
                    msg = ('I would have attacked the uuid => "%s"'
                           ' with attack vector ==> "%s".'
                           % (job[1], job[0]))
                    self.log.info(msg)
        except Exception:
            self.log.critical(traceback.format_exc())
        finally:
            del attack_procs
