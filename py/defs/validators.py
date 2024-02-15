from .samplers import SAMPLERS


def is_positive_prompt(node_id, obj, prompt, extra_data, outputs, input_data_all):
    positive_node_id_list = {}
    for nid, node in prompt.items():
        for sampler_type, field_map in SAMPLERS.items():
            if node["class_type"] == sampler_type:
                positive_node_id = node["inputs"][field_map["positive"]][0]
                positive_node_id_list[nid] = positive_node_id
    return node_id in positive_node_id_list.values()


def is_negative_prompt(node_id, obj, prompt, extra_data, outputs, input_data_all):
    negative_node_id_list = {}
    for nid, node in prompt.items():
        for sampler_type, field_map in SAMPLERS.items():
            if node["class_type"] == sampler_type:
                negative_node_id = node["inputs"][field_map["negative"]][0]
                negative_node_id_list[nid] = negative_node_id
    return node_id in negative_node_id_list.values()
