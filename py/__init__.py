import functools

from .defs.hook_definition import hooks, samplers
from .defs.meta import MetaField
import execution

inputs = {}
current_node_id = -1
current_prompt_id = -1
current_prompt = {}
positive_nodes = {}
negative_nodes = {}


def prefix_function(function, prefunction):
    @functools.wraps(function)
    def run(*args, **kwargs):
        prefunction(*args, **kwargs)
        return function(*args, **kwargs)

    return run


def pre_execute(self, prompt, prompt_id, extra_data, execute_outputs):
    global current_prompt
    global current_prompt_id
    global positive_nodes
    global negative_nodes

    current_prompt = prompt
    current_prompt_id = prompt_id
    inputs[current_prompt_id] = {}
    print("pre_execute")
    print(current_prompt_id)
    positive_nodes, negative_nodes = get_positives_and_negatives(current_prompt)


def pre_get_input_data(*args, **kwargs):
    global current_node_id

    inputs = args[0]
    class_def = args[1]
    unique_id = args[2]
    current_node_id = unique_id
    for node_class, metas in hooks.items():
        if class_def == node_class:
            print(inputs, class_def, unique_id)


def pre_map_node_over_list(*args, **kwargs):
    global current_node_id
    global positive_nodes
    global negative_nodes

    obj, input_data_all, func = args
    for node_class, metas in hooks.items():
        if isinstance(obj, node_class):
            for meta, field_name in metas.items():
                if meta == MetaField.POSITIVE_PROMPT:
                    if current_node_id not in positive_nodes.values():
                        continue
                elif meta == MetaField.NEGATIVE_PROMPT:
                    if current_node_id not in negative_nodes.values():
                        continue

                if meta not in inputs[current_prompt_id]:
                    inputs[current_prompt_id][meta] = []
                value = input_data_all.get(field_name)
                if value is not None:
                    v = value
                    if isinstance(value, list) and len(value) > 0:
                        v = value[0]
                    inputs[current_prompt_id][meta].append((current_node_id, v))
            print(inputs[current_prompt_id])


execution.PromptExecutor.execute = prefix_function(
    execution.PromptExecutor.execute, pre_execute
)
execution.get_input_data = prefix_function(execution.get_input_data, pre_get_input_data)
execution.map_node_over_list = prefix_function(
    execution.map_node_over_list, pre_map_node_over_list
)


def get_positives_and_negatives(prompt):
    positive_node_id_list = {}
    negative_node_id_list = {}
    for node_id, node in prompt.items():
        for sampler_type, field_map in samplers.items():
            if node["class_type"] == sampler_type.__name__:
                positive_node_id = node["inputs"][field_map["positive"]][0]
                negative_node_id = node["inputs"][field_map["negative"]][0]
                positive_node_id_list[node_id] = positive_node_id
                negative_node_id_list[node_id] = negative_node_id
    return positive_node_id_list, negative_node_id_list
