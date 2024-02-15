import functools

from .hook import pre_execute
import execution


# refer. https://stackoverflow.com/a/35758398
def prefix_function(function, prefunction):
    @functools.wraps(function)
    def run(*args, **kwargs):
        prefunction(*args, **kwargs)
        return function(*args, **kwargs)

    return run


execution.PromptExecutor.execute = prefix_function(
    execution.PromptExecutor.execute, pre_execute
)
