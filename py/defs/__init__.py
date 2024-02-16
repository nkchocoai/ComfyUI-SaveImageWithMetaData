import glob
import importlib
import os

from .captures import CAPTURE_FIELD_LIST
from .samplers import SAMPLERS

dir_name = os.path.dirname(os.path.abspath(__file__))
for module_path in glob.glob(dir_name + "/ext/*.py"):
    module_name = os.path.basename(module_path)
    module_name = os.path.splitext(module_name)[0]
    package_name = (
        f"custom_nodes.ComfyUI-SaveImageWithMetaData.py.defs.ext.{module_name}"
    )
    module = importlib.import_module(package_name)
    CAPTURE_FIELD_LIST.update(getattr(module, "CAPTURE_FIELD_LIST", {}))
    SAMPLERS.update(getattr(module, "SAMPLERS", {}))
