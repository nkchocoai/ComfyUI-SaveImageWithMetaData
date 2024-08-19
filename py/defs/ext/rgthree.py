# https://github.com/rgthree/rgthree-comfy
from ..meta import MetaField
from ..formatters import calc_lora_hash


def get_lora_model_name(node_id, obj, prompt, extra_data, outputs, input_data):
    return get_lora_data(input_data, "lora")


def get_lora_model_hash(node_id, obj, prompt, extra_data, outputs, input_data):
    return [
        calc_lora_hash(model_name, input_data)
        for model_name in get_lora_data(input_data, "lora")
    ]


def get_lora_strength(node_id, obj, prompt, extra_data, outputs, input_data):
    return get_lora_data(input_data, "strength")


def get_lora_data(input_data, attribute):
    return [
        v[0][attribute]
        for k, v in input_data[0].items()
        if k.startswith("lora_") and v[0]["on"]
    ]


def get_lora_model_name_stack(node_id, obj, prompt, extra_data, outputs, input_data):
    return get_lora_data_stack(input_data, "lora")


def get_lora_model_hash_stack(node_id, obj, prompt, extra_data, outputs, input_data):
    return [
        calc_lora_hash(model_name, input_data)
        for model_name in get_lora_data_stack(input_data, "lora")
    ]


def get_lora_strength_stack(node_id, obj, prompt, extra_data, outputs, input_data):
    return get_lora_data_stack(input_data, "strength")


def get_lora_data_stack(input_data, attribute):
    return [
        v[0]
        for k, v in input_data[0].items()
        if k.startswith(attribute + "_") and v[0] != "None"
    ]


CAPTURE_FIELD_LIST = {
    "Power Lora Loader (rgthree)": {
        MetaField.LORA_MODEL_NAME: {"selector": get_lora_model_name},
        MetaField.LORA_MODEL_HASH: {"selector": get_lora_model_hash},
        MetaField.LORA_STRENGTH_MODEL: {"selector": get_lora_strength},
        MetaField.LORA_STRENGTH_CLIP: {"selector": get_lora_strength},
    },
    "Lora Loader Stack (rgthree)": {
        MetaField.LORA_MODEL_NAME: {"selector": get_lora_model_name_stack},
        MetaField.LORA_MODEL_HASH: {"selector": get_lora_model_hash_stack},
        MetaField.LORA_STRENGTH_MODEL: {"selector": get_lora_strength_stack},
        MetaField.LORA_STRENGTH_CLIP: {"selector": get_lora_strength_stack},
    },
}
