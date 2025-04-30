# https://github.com/miaoshouai/ComfyUI-Miaoshouai-Tagger
from ..meta import MetaField
from ..formatters import calc_model_hash, calc_lora_hash, convert_skip_clip

SAMPLERS = {
}

CAPTURE_FIELD_LIST = {
    "Miaoshouai_SaveTags": {
        MetaField.POSITIVE_PROMPT: {"field_name": "captions"},
    },
    "Miaoshouai_Flux_CLIPTextEncode": {
        MetaField.POSITIVE_PROMPT: {"field_name": "caption"},
        MetaField.CFG:             {"field_name": "guidance"},
    },
    "Miaoshouai_Caption_Analyzer": {
        MetaField.POSITIVE_PROMPT: {"field_name": "analyze"},
    },
}
