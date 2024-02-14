from enum import Enum


class MetaField(Enum):
    MODEL_NAME = 0
    POSITIVE_PROMPT = 10
    NEGATIVE_PROMPT = 11
    SEED = 20
    STEPS = 21
    CFG = 22
    SAMPLER_NAME = 23
    SCHEDULER = 24
    IMAGE_WIDTH = 30
    IMAGE_HEIGHT = 31
