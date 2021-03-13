import logging
from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.tasks.files import write_file
import os

def save_show(task: Task, command : str, filename_mark : str ) -> Result:
      
    show_result = task.run(
      task=netmiko_send_command, 
      command_string=command,
      enable=True,
      delay_factor=5,
      max_loops=6000
    )
    task.host['show_result'] = show_result.result
    
    isExist = os.path.exists(f"output/{command}-{filename_mark}")
    if not isExist:
          os.mkdir(f"output/{command}-{filename_mark}")
          
    task.run(
      task=write_file,
      filename=f"output/{command}-{filename_mark}/{task.host}.cfg" ,
      content=task.host['show_result']  
    )
    
    return Result(
      host = task.host,
      result = f"output/{command}-{filename_mark}/{task.host}.cfg" ,
      severity_level=logging.WARNING
    )
    

    