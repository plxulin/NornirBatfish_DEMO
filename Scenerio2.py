
from nornir import InitNornir
from nornir.core import configuration
from nornir.plugins.runners import ThreadedRunner, SerialRunner
from nornir.core.plugins.inventory import InventoryPluginRegister
import logging

from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from nornir_napalm.plugins.tasks import *
from nornir_netmiko.tasks import *
from nornir_jinja2.plugins.tasks import *
from nornir_netbox.plugins.inventory import NetBoxInventory2
from mytasks import *
from mytasks.batfishTasks import *

InventoryPluginRegister.register("SerialRunner", SerialRunner)
InventoryPluginRegister.register("ThreadedRunner", ThreadedRunner)
InventoryPluginRegister.register("NetBoxInventory2", NetBoxInventory2)

nr = InitNornir(
    config_file='config.yaml',
    dry_run=False)

nr = nr.filter(name = 'localhost')


def batfish_tasks(task):
    task.run(
        task = BF_session,
        host = "localhost",
    )
    task.run(
        task = BF_init,
        network_name = 'forwarding_change_validation',
        snapshot_name = 'base',
        snapshot_dir = './batfish_snapshot/forwarding-change-validation/base',
        overwrite = True,
        
    )

result = nr.run(
    task = batfish_tasks,
    on_failed=True
)
print_result(result, severity_level=logging.INFO)


result = nr.run(
    task = BF_assert_flows_exist,
    name = "CHECK HTTP FROM BORDER1 TO HOST-WWW EXISTS",
    on_failed = True,
    debug = False,
    
    startLocation = "@enter(/border1/[GigabitEthernet0/0])",
    dstIps = '/host-www/',
    srcIps = '0.0.0.0/0',
    applications='HTTP',
    actions = 'SUCCESS',   
    
)
print_result(result, severity_level=logging.INFO)

result = nr.run(
    task = BF_assert_flows_exist,
    name = "CHECK HTTP FROM BORDER2 TO HOST-WWW EXISTS",
    on_failed = True,
    debug = False,
    
    startLocation = "@enter(/border2/[GigabitEthernet0/0])",
    dstIps = '/host-www/',
    srcIps = '0.0.0.0/0',
    applications='HTTP',
    actions = 'SUCCESS',   
    
)
print_result(result, severity_level=logging.INFO)

# DEBUG!!!
#
# result = nr.run(
#     task = BF_traceroute ,
#     name = "DEBUG HTTP traffic from Border to HOST-WWW",
#     on_failed = True,

#     startLocation = "@enter(/border/[GigabitEthernet0/0])",
#     dstIps = '/host-www/',
#     # srcIps = '0.0.0.0/0',
#     applications='HTTP',
# )
# print_result(result, severity_level=logging.INFO)

result = nr.run(
    task = BF_assert_flows_exist,
    name = "CHECK ALL HTTP TRAFFIC FAILURE ON REACH TO HOST-WWW EXISTS",
    on_failed = True,
    debug = False,
    
    startLocation = "@enter(/border/[GigabitEthernet0/0])",
    dstIps = '/host-www/',
    srcIps = '0.0.0.0/0',
    applications='HTTP',
    actions = 'FAILURE',   
    
)
print_result(result, severity_level=logging.INFO)


result = nr.run(
    task = BF_assert_flows_exist,
    name = "CHECK HTTP TRAFFIC REACH TO HOST-DB EXIST",
    on_failed = True,
    debug = True,
    
    startLocation = "@enter(/border/[GigabitEthernet0/0])",
    dstIps = '/host-db/',
    srcIps = '0.0.0.0/0',
    applications='HTTP',
    actions = 'SUCCESS',   
    
)
print_result(result, severity_level=logging.INFO)