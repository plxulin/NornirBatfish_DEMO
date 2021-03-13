import re
from typing import Optional, Any
from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command
import pandas as pd
from pybatfish.client.commands import *
from pybatfish.datamodel import *
from pybatfish.datamodel.answer import *
from pybatfish.datamodel.flow import *
from pybatfish.question import *
from pybatfish.question import bfq
import logging
from pprint import pformat, pprint

    
def BF_session(task: Task, host='127.0.0.1' ) -> Result:
    logging.getLogger("pybatfish").setLevel(logging.CRITICAL)
    bf_session.host = host
    load_questions()
    return Result(
        host=task.host, 
        result=f"set up bf service ip : {task.host.hostname}"
        )

def BF_init(
    task: Task, 
    network_name: str, 
    snapshot_name: str, 
    snapshot_dir: str, 
    overwrite: bool
    ) -> Result:
    """
    init batfish
    """
    bf_set_network(network_name)
    bf_init_snapshot(snapshot_dir, name=snapshot_name, overwrite=overwrite)
    result = bfq.fileParseStatus().answer()

    result={
        'Results': result['answerElements'][0]['rows'],
        'Summary': result['answerElements'][0]['summary'],
        }
    
    return Result(
        host=task.host, 
        result=result
        )

def BF_initIssues(task: Task) -> Result :
    result = bfq.initIssues().answer()
    result={
        'Results': result['answerElements'][0]['rows'],
        'Summary': result['answerElements'][0]['summary'],
        }
    
    return Result(
        host=task.host, 
        result=result
        )
    

def BF_assert_no_undefined_referenes(task: Task) -> Result:
    result = bfq.undefinedReferences().answer()
    
    result = {
            'Results': result['answerElements'][0]['rows'],
            'Summary': result['answerElements'][0]['summary'],
            }
    
    assert result['Summary']['numResults'] == 0 ,'\n'+pformat(result)
    return Result(
        host=task.host, 
        result=result
        )

def BF_assert_no_unusedStructures(task: Task) -> Result:
    result = bfq.unusedStructures().answer()
    
    result = {
            'Results': result['answerElements'][0]['rows'],
            'Summary': result['answerElements'][0]['summary'],
            }
    
    assert result['Summary']['numResults'] == 0 ,'\n'+pformat(result)
    return Result(
        host=task.host, 
        result=result
        )

def BF_traceroute(
    task: Task,
    startLocation: str = None, 
    ignoreFilters: bool = False,
    **kwargs
    ) -> Result:
    
    result = bfq.traceroute(
        startLocation = startLocation,
        headers = HeaderConstraints(**kwargs),
        ignoreFilters = ignoreFilters
    ).answer()
    
    result = {
            'Results': result['answerElements'][0]['rows'],
            'Summary': result['answerElements'][0]['summary'],
            }

    return Result(
        host=task.host, 
        result=result
    )
    

def BF_assert_flows_exist(
    task: Task,
    debug: bool = False,
    startLocation: str = None, 
    endLocation: str = None, 
    transitLocations: str = None, 
    forbiddenLocations: str = None,
    actions: str = 'SUCCESS',
    **kwargs
    ) -> Result:
    
    result = bfq.reachability(
        pathConstraints=PathConstraints(
            startLocation= startLocation, 
            endLocation=endLocation, 
            transitLocations=transitLocations, 
            forbiddenLocations=forbiddenLocations,
            ),
        
        headers=HeaderConstraints(**kwargs),
        actions=actions
        ).answer()

    result = {
            'Results': result['answerElements'][0]['rows'],
            'Summary': result['answerElements'][0]['summary'],
            }

    assert result['Results'] != [], "NO FLOW FOUNDED"
    
    if not debug:
        result = 'FLOW EXISTS'

    return Result(
        host = task.host, 
        result = result,
    )
    