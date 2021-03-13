from nornir.core.task import Result, Task

def hello_world(task: Task):

    return Result(
        host=task.host,
        result=f"{task.host} says hello world!"
    )

def say(task: Task, text: str):
    return Result(
        host=task.host,
        result=f"{task.host.name} says {text}"
    )

def count(task: Task, number: int):
    return Result(
        host=task.host,
        result=f"{[n for n in range(0, number)]}"
    )
    
def greet_and_count(task: Task, number: int):
    """This function is for learning of how to group tasks

    Args:
        task (Task): [description]
        number (int): count times

    Returns:
        Result: [description]
    """    
    task.run(
        name="Greeting is the polite thing to do",
        task=say,
        text="hi!",
    )

    task.run(
        name="Counting beans",
        task=count,
        number=number,
    )
    task.run(
        name="We should say bye too",
        task=say,
        text="bye!",
    )

    # let's inform if we counted even or odd times
    even_or_odds = "even" if number % 2 == 1 else "odd"
    return Result(
        host=task.host,
        result=f"{task.host} counted {even_or_odds} times!",
    )