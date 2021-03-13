from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command

def connection_check(task: Task ) -> Result:
    task.run(
      task=netmiko_send_command, 
      command_string=' ',
      delay_factor=5,
      max_loops=6000
    )
    
    
    

