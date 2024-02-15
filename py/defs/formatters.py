import hashlib

import folder_paths

cache_model_hash = {}


def calc_model_hash(model_name):
    if model_name in cache_model_hash:
        return cache_model_hash[model_name]

    filename = folder_paths.get_full_path("checkpoints", model_name)
    sha256_hash = hashlib.sha256()

    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    model_hash = sha256_hash.hexdigest()[:10]

    cache_model_hash[model_name] = model_hash
    return model_hash
