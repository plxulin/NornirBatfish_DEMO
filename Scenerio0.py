
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
    
    task.run(
        task = BF_initIssues 
    )


result = nr.run(
    task = batfish_tasks,
    on_failed=True
)
print_result(result, severity_level=logging.INFO)

result = nr.run(
    task = BF_assert_no_undefined_referenes,
    on_failed=True
)
print_result(result, severity_level=logging.INFO)

result = nr.run(
    task = BF_assert_no_unusedStructures,
    on_failed=True
)
print_result(result, severity_level=logging.INFO)
