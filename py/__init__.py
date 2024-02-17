import functools

from .hook import pre_execute, pre_recursive_execute
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


execution.recursive_execute = prefix_function(
    execution.recursive_execute, pre_recursive_execute
)
