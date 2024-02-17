# https://github.com/nkchocoai/ComfyUI-SizeFromPresets/
from ..meta import MetaField


def get_width(preset, input_data):
    return preset.split("x")[0].strip()


def get_height(preset, input_data):
    return preset.split("x")[1].strip()


CAPTURE_FIELD_LIST = {
    "EmptyLatentImageFromPresetsSD15": {
        MetaField.IMAGE_WIDTH: {"field_name": "preset", "format": get_width},
        MetaField.IMAGE_HEIGHT: {"field_name": "preset", "format": get_height},
    },
    "EmptyLatentImageFromPresetsSDXL": {
        MetaField.IMAGE_WIDTH: {"field_name": "preset", "format": get_width},
        MetaField.IMAGE_HEIGHT: {"field_name": "preset", "format": get_height},
    },
    # TODO RandomEmptyLatentImageFromPresetsSD..
}
