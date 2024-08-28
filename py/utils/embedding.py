import os

from comfy.sd1_clip import expand_directory_list


# refer. https://github.com/comfyanonymous/ComfyUI/blob/dccca1daa5af1954d55918f365e83a3331019549/comfy/sd1_clip.py#L284-L309
def get_embedding_file_path(embedding_name, clip):
    embedding_directory = clip.embedding_directory
    if isinstance(embedding_directory, str):
        embedding_directory = [embedding_directory]

    embedding_directory = expand_directory_list(embedding_directory)

    valid_file = None
    for embed_dir in embedding_directory:
        embed_path = os.path.abspath(os.path.join(embed_dir, embedding_name))
        embed_dir = os.path.abspath(embed_dir)
        try:
            if os.path.commonpath((embed_dir, embed_path)) != embed_dir:
                continue
        except Exception:
            continue
        if not os.path.isfile(embed_path):
            extensions = [".safetensors", ".pt", ".bin"]
            for x in extensions:
                t = embed_path + x
                if os.path.isfile(t):
                    valid_file = t
                    break
        else:
            valid_file = embed_path
        if valid_file is not None:
            break

    return valid_file
