import os

import folder_paths

from ..utils.hash import calc_hash
from ..utils.embedding import get_embedding_file_path

from comfy.sd1_clip import escape_important, token_weights, unescape_important
from comfy.sd1_clip import SD1Tokenizer
from comfy.text_encoders.sd2_clip import SD2Tokenizer
from comfy.text_encoders.sd3_clip import SD3Tokenizer
from comfy.text_encoders.flux import FluxTokenizer
from comfy.sdxl_clip import SDXLTokenizer

cache_model_hash = {}


def calc_model_hash(model_name, input_data):
    filename = folder_paths.get_full_path("checkpoints", model_name)
    return calc_hash(filename)


def calc_vae_hash(model_name, input_data):
    filename = folder_paths.get_full_path("vae", model_name)
    return calc_hash(filename)


def calc_lora_hash(model_name, input_data):
    filename = folder_paths.get_full_path("loras", model_name)
    return calc_hash(filename)


def calc_unet_hash(model_name, input_data):
    filename = folder_paths.get_full_path("unet", model_name)
    return calc_hash(filename)


def convert_skip_clip(stop_at_clip_layer, input_data):
    return stop_at_clip_layer * -1


def get_scaled_width(scaled_by, input_data):
    samples = input_data[0]["samples"][0]["samples"]
    return round(samples.shape[3] * scaled_by * 8)


def get_scaled_height(scaled_by, input_data):
    samples = input_data[0]["samples"][0]["samples"]
    return round(samples.shape[2] * scaled_by * 8)


def extract_embedding_names(text, input_data):
    embedding_names, _ = _extract_embedding_names(text, input_data)

    return [os.path.basename(embedding_name) for embedding_name in embedding_names]


def extract_embedding_hashes(text, input_data):
    embedding_names, clip = _extract_embedding_names(text, input_data)
    embedding_hashes = []
    for embedding_name in embedding_names:
        embedding_file_path = get_embedding_file_path(embedding_name, clip)
        embedding_hashes.append(calc_hash(embedding_file_path))

    return embedding_hashes


def _extract_embedding_names(text, input_data):
    embedding_identifier = "embedding:"
    clip_ = input_data[0]["clip"][0]
    clip = None
    if clip_ is not None:
        tokenizer = clip_.tokenizer
        if isinstance(tokenizer, SD1Tokenizer):
            clip = tokenizer.clip_l
        elif isinstance(tokenizer, SD2Tokenizer):
            clip = tokenizer.clip_h
        elif isinstance(tokenizer, SDXLTokenizer):
            clip = tokenizer.clip_l
        elif isinstance(tokenizer, SD3Tokenizer):
            clip = tokenizer.clip_l
        elif isinstance(tokenizer, FluxTokenizer):
            clip = tokenizer.clip_l
        if clip is not None and hasattr(clip, "embedding_identifier"):
            embedding_identifier = clip.embedding_identifier
    if not isinstance(text, str):
        text = "".join(str(item) if item is not None else "" for item in text)
    text = escape_important(text)
    parsed_weights = token_weights(text, 1.0)

    # tokenize words
    embedding_names = []
    for weighted_segment, weight in parsed_weights:
        to_tokenize = unescape_important(weighted_segment).replace("\n", " ").split(" ")
        to_tokenize = [x for x in to_tokenize if x != ""]
        for word in to_tokenize:
            # find an embedding, deal with the embedding
            if (
                word.startswith(embedding_identifier)
                and clip.embedding_directory is not None
            ):
                embedding_name = word[len(embedding_identifier) :].strip("\n")
                embedding_names.append(embedding_name)

    return embedding_names, clip
