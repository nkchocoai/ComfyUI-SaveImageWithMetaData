current_prompt = {}
current_extra_data = {}
prompt_executer = None


def pre_execute(self, prompt, prompt_id, extra_data, execute_outputs):
    global current_prompt
    global current_extra_data
    global prompt_executer

    current_prompt = prompt
    current_extra_data = extra_data
    prompt_executer = self
