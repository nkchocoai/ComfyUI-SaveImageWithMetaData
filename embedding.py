import os
from comfy.sd1_clip import expand_directory_list

def get_embedding_file_path(embedding_name, clip):
    """
    Resolves the file path for an embedding by searching directories and checking file extensions.

    Args:
        embedding_name (str): The name of the embedding file (without an extension).
        clip (object): An object containing the attribute `embedding_directory`, 
                       which specifies directories to search.

    Returns:
        str or None: Full path to the embedding file if found, otherwise None.
    """
    # Validate embedding_directory
    embedding_directory = getattr(clip, "embedding_directory", None)
    if not embedding_directory:
        raise ValueError("The 'embedding_directory' attribute in the clip object is None or empty.")
    
    if isinstance(embedding_directory, str):
        embedding_directory = [embedding_directory]

    # Expand directories using the provided function
    try:
        embedding_directory = expand_directory_list(embedding_directory)
    except Exception as e:
        raise ValueError(f"Error expanding directory list: {e}")

    if not embedding_directory:
        raise ValueError("No valid directories found after expansion.")

    valid_file = None
    extensions = [".safetensors", ".pt", ".bin"]

    for embed_dir in embedding_directory:
        embed_dir = os.path.abspath(embed_dir)
        if not os.path.isdir(embed_dir):
            # Skip invalid directories
            continue

        # Construct the absolute path for the embedding name
        embed_path = os.path.abspath(os.path.join(embed_dir, embedding_name))
        
        try:
            # Ensure embed_path is within embed_dir (security check)
            if os.path.commonpath([embed_dir, embed_path]) != embed_dir:
                continue
        except Exception as e:
            # Skip this directory on exception (e.g., invalid path comparison)
            continue

        # Check if the file exists with or without extensions
        if os.path.isfile(embed_path):
            valid_file = embed_path
        else:
            for ext in extensions:
                candidate_path = embed_path + ext
                if os.path.isfile(candidate_path):
                    valid_file = candidate_path
                    break

        # Stop searching if a valid file is found
        if valid_file:
            break

    return valid_file
