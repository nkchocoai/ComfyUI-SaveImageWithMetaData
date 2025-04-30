#https://github.com/Light-x02/ComfyUI-FluxSettingsNode
from ..meta import MetaField
from ..formatters import calc_model_hash, calc_lora_hash, convert_skip_clip


SAMPLERS = {
    "FluxSettingsNode": {
        "positive": "conditioning.positive",
        "negative": "conditioning.negative",
    },
}


CAPTURE_FIELD_LIST = {
    "FluxSettingsNode": {
        MetaField.CFG: {"field_name": "guidance"},  
        MetaField.SAMPLER_NAME: {"field_name": "sampler_name"},  
        MetaField.SCHEDULER: {"field_name": "scheduler"},  
        MetaField.STEPS: {"field_name": "steps"},  
        MetaField.SEED: {"field_name": "noise_seed"},
        MetaField.POSITIVE_PROMPT: {"field_name": "conditioning.positive"},  
        MetaField.NEGATIVE_PROMPT: {"field_name": "conditioning.negative"},  
    },
}
