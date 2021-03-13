from nornir.core.task import Result, Task
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.files import write_file
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_netmiko.tasks import netmiko_send_config

def render_configs(task, template_name):
    template_path = f"templates/{task.host.platform}/"
    template = template_name
    result = task.run(
        task=template_file, template=template, path=template_path, **task.host
    )
    rendered_config = result[0].result
    task.host["rendered_config"] = rendered_config


def write_configs(task, config_name):
    cfg_path = f"configs/{task.host.platform}/"
    filename = f"{cfg_path}{task.host.name}_{config_name}"
    content = task.host["rendered_config"]
    task.run(task=write_file, filename=filename, content=content)


def deploy_configs(task, config_name):
    filename = f"configs/{task.host.platform}/{task.host.name}_{config_name}"
    # with open(filename, "r") as f:
    #     cfg = f.read()
    result = task.run(task=netmiko_send_config, config_file=filename)
    return result

def jinjia2_write_deploy(task, template_n):
    render_result = task.run(task=render_configs, template_name=template_n+'.j2')
    write_result = task.run(task=write_configs, config_name=template_n)
    deploy_result = task.run(task=deploy_configs, config_name=template_n)
