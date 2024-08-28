from .py.nodes.node import SaveImageWithMetaData, CreateExtraMetaData

NODE_CLASS_MAPPINGS = {
    "SaveImageWithMetaData": SaveImageWithMetaData,
    "CreateExtraMetaData": CreateExtraMetaData,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageWithMetaData": "Save Image With Metadata",
    "CreateExtraMetaData": "Create Extra MetaData",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
