import traceback
import random
import shelve
import datetime
import tempfile
import os

# Import bookofnova
from bookofnova import authentication, computelib

# Local Imports
from psycorax import info, generators


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
        self.now = datetime.datetime.now()
        self.db_file = '%s%s%s.dbm' % (tempfile.gettempdir(),
                                       os.sep,
                                       info.__appname__)
        # Set Initial Arguments
        self.m_args = m_args

        # Set the Log Handler
        self.log = output

        # Prep Nova For Use
        self.nova = computelib.NovaCommands(m_args=self.m_args,
                                            output=self.log)
    def show_report(self, date=None):
        _db = shelve.open(self.db_file, flag='r')
        if date:
            if date in _db:
                print('REPORT FOR "%s"\t:' % date)
                for inst in _db[date]:
                    msg = ('Instance UUID => "%s"\n'
                           'Attack vector ==> "%s"\n'
                           'Time ==> "%s"' % inst)
                    print msg
            else:
                print('%s not found in DB' % date)
        else:
            for day in _db.keys():
                print('REPORT FOR "%s"\t:' % day)
                for inst in _db[day]:
                    msg = ('Instance UUID => "%s"\n'
                           'Attack vector ==> "%s"\n'
                           'Time ==> "%s"' % inst)
                    print msg
        _db.close()

    def record_actions(self, action):
        today = self.now.strftime("%Y%m%d-%H%M")
        _db = shelve.open(self.db_file, writeback=True)
        if not today in _db:
            _db[today] = []
            _db[today].append(action)
        else:
            _db[today].append(action)
        _db.sync()
        _db.close()

    def authenticate(self):
        """
        Authenticate against an OpenStack API if not 200 Raise an exception
        """
        try:
            self.m_args = self.nova.auth()
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
            if 'amebaMon' in inst['metadata']:
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
            psyco_path.update({'FAB': fabs.run_attack})
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
            elif self.m_args['cc_attack'] <= 1:
                if node_count == 1:
                    num_nodes = 1
                else:
                    num_nodes = random.randrange(0, node_count)
            elif self.m_args['cc_attack'] == 1:
                num_nodes = 1
            else:
                if self.m_args['cc_attack'] > node_count:
                    self.m_args['cc_attack'] = node_count
                num_nodes = random.randrange(1, self.m_args['cc_attack'])
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
                inst_info = (node['id'],
                             destructive,
                             self.now.strftime("%Y%m%d-%H%M%S"))
                msg = ('Instance UUID => "%s"\n'
                       'Attack vector ==> "%s"\n'
                       'Time ==> "%s"'
                       % inst_info)
                self.record_actions(action=inst_info)
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
