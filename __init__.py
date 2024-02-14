from .py.nodes.node import SaveImageWithMetaData

NODE_CLASS_MAPPINGS = {
    "SaveImageWithMetaData": SaveImageWithMetaData,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageWithMetaData": "Save Image With Metadata",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
