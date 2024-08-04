from collections import deque

from .samplers import SAMPLERS


def is_positive_prompt(node_id, obj, prompt, extra_data, outputs, input_data_all):
    return node_id in _get_node_id_list(prompt, "positive")


def is_negative_prompt(node_id, obj, prompt, extra_data, outputs, input_data_all):
    return node_id in _get_node_id_list(prompt, "negative")


def _get_node_id_list(prompt, field_name):
    node_id_list = {}
    for nid, node in prompt.items():
        for sampler_type, field_map in SAMPLERS.items():
            if node["class_type"] == sampler_type:
                # There are nodes between "KSampler" and "CLIP Text Encode" in the SD3 workflow
                d = deque()
                if field_name in field_map and field_map[field_name] in node["inputs"]:
                    d.append(node["inputs"][field_map[field_name]][0])
                while len(d) > 0:
                    nid2 = d.popleft()
                    class_type = prompt[nid2]["class_type"]
                    if class_type == "CLIPTextEncode":
                        node_id_list[nid] = nid2
                        break
                    inputs = prompt[nid2]["inputs"]
                    for k, v in inputs.items():
                        if isinstance(v, list):
                            d.append(v[0])

    return node_id_list.values()
