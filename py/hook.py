current_prompt = {}
current_extra_data = {}
prompt_executer = None
current_node_id = -1


def pre_execute(self, prompt, prompt_id, extra_data, execute_outputs):
    global current_prompt
    global current_extra_data
    global prompt_executer

    current_prompt = prompt
    current_extra_data = extra_data
    prompt_executer = self


def pre_recursive_execute(
    server,
    prompt,
    outputs,
    current_item,
    extra_data,
    executed,
    prompt_id,
    outputs_ui,
    object_storage,
):
    global current_node_id

    current_node_id = current_item
