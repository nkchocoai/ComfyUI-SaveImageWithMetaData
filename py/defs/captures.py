from .meta import MetaField
from .validators import is_positive_prompt, is_negative_prompt
from .formatters import (
    calc_model_hash,
    convert_skip_clip,
    get_scaled_width,
    get_scaled_height,
)


CAPTURE_FIELD_LIST = {
    "CheckpointLoaderSimple": {
        MetaField.MODEL_NAME: {"field_name": "ckpt_name"},
        MetaField.MODEL_HASH: {"field_name": "ckpt_name", "format": calc_model_hash},
    },
    "CLIPSetLastLayer": {
        MetaField.CLIP_SKIP: {
            "field_name": "stop_at_clip_layer",
            "format": convert_skip_clip,
        },
    },
    "EmptyLatentImage": {
        MetaField.IMAGE_WIDTH: {"field_name": "width"},
        MetaField.IMAGE_HEIGHT: {"field_name": "height"},
    },
    "CLIPTextEncode": {
        MetaField.POSITIVE_PROMPT: {
            "field_name": "text",
            "validate": is_positive_prompt,
        },
        MetaField.NEGATIVE_PROMPT: {
            "field_name": "text",
            "validate": is_negative_prompt,
        },
    },
    "KSampler": {
        MetaField.SEED: {"field_name": "seed"},
        MetaField.STEPS: {"field_name": "steps"},
        MetaField.CFG: {"field_name": "cfg"},
        MetaField.SAMPLER_NAME: {"field_name": "sampler_name"},
        MetaField.SCHEDULER: {"field_name": "scheduler"},
    },
    "KSamplerAdvanced": {
        MetaField.SEED: {"field_name": "noise_seed"},
        MetaField.STEPS: {"field_name": "steps"},
        MetaField.CFG: {"field_name": "cfg"},
        MetaField.SAMPLER_NAME: {"field_name": "sampler_name"},
        MetaField.SCHEDULER: {"field_name": "scheduler"},
    },
    "LatentUpscale": {
        MetaField.IMAGE_WIDTH: {"field_name": "width"},
        MetaField.IMAGE_HEIGHT: {"field_name": "height"},
    },
    "LatentUpscaleBy": {
        MetaField.IMAGE_WIDTH: {"field_name": "scale_by", "format": get_scaled_width},
        MetaField.IMAGE_HEIGHT: {
            "field_name": "scale_by",
            "format": get_scaled_height,
        },
    },
}
