from nodes import CLIPTextEncode, KSampler
from .meta import MetaField

samplers = {
    KSampler: {
        "positive": "positive",
        "negative": "negative",
    },
}

hooks = {
    CLIPTextEncode: {
        MetaField.POSITIVE_PROMPT: "text",
        MetaField.NEGATIVE_PROMPT: "text",
    },
    KSampler: {
        MetaField.SEED: "seed",
        MetaField.STEPS: "steps",
        MetaField.CFG: "cfg",
        MetaField.SAMPLER_NAME: "sampler_name",
        MetaField.SCHEDULER: "scheduler",
    },
}
