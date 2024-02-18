import os

import folder_paths

from ..utils.hash import calc_hash
from ..utils.embedding import get_embedding_file_path

from comfy.sd1_clip import escape_important, token_weights, unescape_important
from comfy.sdxl_clip import SDXLTokenizer

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


def extract_embedding_names(text, input_data):
    embedding_names, _ = _extract_embedding_names(text, input_data)

    return [os.path.basename(embedding_name) for embedding_name in embedding_names]


def extract_embedding_hashes(text, input_data):
    embedding_names, tokenizer = _extract_embedding_names(text, input_data)
    embedding_hashes = []
    for embedding_name in embedding_names:
        embedding_file_path = get_embedding_file_path(embedding_name, tokenizer)
        embedding_hashes.append(calc_hash(embedding_file_path))

    return embedding_hashes


def _extract_embedding_names(text, input_data):
    clip = input_data["clip"][0]
    tokenizer = clip.tokenizer
    if isinstance(tokenizer, SDXLTokenizer):
        tokenizer = tokenizer.clip_l
    text = escape_important(text)
    parsed_weights = token_weights(text, 1.0)

    # tokenize words
    embedding_names = []
    for weighted_segment, weight in parsed_weights:
        to_tokenize = unescape_important(weighted_segment).replace("\n", " ").split(" ")
        to_tokenize = [x for x in to_tokenize if x != ""]
        for word in to_tokenize:
            # if we find an embedding, deal with the embedding
            if (
                word.startswith(tokenizer.embedding_identifier)
                and tokenizer.embedding_directory is not None
            ):
                embedding_name = word[len(tokenizer.embedding_identifier) :].strip("\n")

                embedding_names.append(embedding_name)

    return embedding_names, tokenizer
