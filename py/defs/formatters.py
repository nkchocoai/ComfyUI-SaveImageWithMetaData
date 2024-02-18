import folder_paths

from ..utils.hash import calc_hash

cache_model_hash = {}


def calc_model_hash(model_name, input_data):
    filename = folder_paths.get_full_path("checkpoints", model_name)
    return calc_hash(filename)


def calc_lora_hash(model_name, input_data):
    filename = folder_paths.get_full_path("loras", model_name)
    return calc_hash(filename)


def convert_skip_clip(stop_at_clip_layer, input_data):
    return stop_at_clip_layer * -1


def get_scaled_width(scaled_by, input_data):
    samples = input_data["samples"][0]["samples"]
    return round(samples.shape[3] * scaled_by * 8)


def get_scaled_height(scaled_by, input_data):
    samples = input_data["samples"][0]["samples"]
    return round(samples.shape[2] * scaled_by * 8)
