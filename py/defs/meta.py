from enum import IntEnum


class MetaField(IntEnum):
    MODEL_NAME = 0
    MODEL_HASH = 1
    POSITIVE_PROMPT = 10
    NEGATIVE_PROMPT = 11
    SEED = 20
    STEPS = 21
    CFG = 22
    SAMPLER_NAME = 23
    SCHEDULER = 24
    IMAGE_WIDTH = 30
    IMAGE_HEIGHT = 31
