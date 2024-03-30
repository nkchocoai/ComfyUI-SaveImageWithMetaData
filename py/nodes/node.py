import json
import os
import re

from datetime import datetime

from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np

import folder_paths
from comfy.cli_args import args

from .base import BaseNode

from ..capture import Capture
from .. import hook
from ..trace import Trace

from ..defs.combo import SAMPLER_SELECTION_METHOD


# refer. https://github.com/comfyanonymous/ComfyUI/blob/38b7ac6e269e6ecc5bdd6fefdfb2fb1185b09c9d/nodes.py#L1411
class SaveImageWithMetaData(BaseNode):
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "sampler_selection_method": (SAMPLER_SELECTION_METHOD,),
                "sampler_selection_node_id": (
                    "INT",
                    {"default": 0, "min": 0, "max": 999999999, "step": 1},
                ),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    pattern_format = re.compile(r"(%[^%]+%)")

    def save_images(
        self,
        images,
        filename_prefix="ComfyUI",
        sampler_selection_method=SAMPLER_SELECTION_METHOD[0],
        sampler_selection_node_id=0,
        prompt=None,
        extra_pnginfo=None,
    ):
        pnginfo_dict_src = self.gen_pnginfo(
            sampler_selection_method, sampler_selection_node_id
        )
        results = list()
        for index, image in enumerate(images):
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            pnginfo_dict = pnginfo_dict_src.copy()
            if len(images) >= 2:
                pnginfo_dict["Batch index"] = index
                pnginfo_dict["Batch size"] = len(images)

            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if pnginfo_dict:
                    metadata.add_text(
                        "parameters", Capture.gen_parameters_str(pnginfo_dict)
                    )
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_prefix = self.format_filename(filename_prefix, pnginfo_dict)
            output_path = os.path.join(self.output_dir, filename_prefix)
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            (
                full_output_folder,
                filename,
                counter,
                subfolder,
                filename_prefix,
            ) = folder_paths.get_save_image_path(
                filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
            )
            file = f"{filename}_{counter:05}_.png"

            img.save(
                os.path.join(full_output_folder, file),
                pnginfo=metadata,
                compress_level=self.compress_level,
            )
            results.append(
                {"filename": file, "subfolder": subfolder, "type": self.type}
            )
            counter += 1

        return {"ui": {"images": results}}

    @classmethod
    def gen_pnginfo(cls, sampler_selection_method, sampler_selection_node_id):
        # get all node inputs
        inputs = Capture.get_inputs()

        # get sampler node before this node
        trace_tree_from_this_node = Trace.trace(
            hook.current_save_image_node_id, hook.current_prompt
        )
        inputs_before_this_node = Trace.filter_inputs_by_trace_tree(
            inputs, trace_tree_from_this_node
        )
        sampler_node_id = Trace.find_sampler_node_id(
            trace_tree_from_this_node,
            sampler_selection_method,
            sampler_selection_node_id,
        )

        # get inputs before sampler node
        trace_tree_from_sampler_node = Trace.trace(sampler_node_id, hook.current_prompt)
        inputs_before_sampler_node = Trace.filter_inputs_by_trace_tree(
            inputs, trace_tree_from_sampler_node
        )

        # generate PNGInfo from inputs
        pnginfo_dict = Capture.gen_pnginfo_dict(
            inputs_before_sampler_node, inputs_before_this_node
        )
        return pnginfo_dict

    @classmethod
    def format_filename(cls, filename, pnginfo_dict):
        result = re.findall(cls.pattern_format, filename)
        for segment in result:
            parts = segment.replace("%", "").split(":")
            key = parts[0]
            if key == "seed":
                filename = filename.replace(segment, str(pnginfo_dict.get("Seed", "")))
            elif key == "width":
                w = pnginfo_dict.get("Size", "x").split("x")[0]
                filename = filename.replace(segment, str(w))
            elif key == "height":
                w = pnginfo_dict.get("Size", "x").split("x")[1]
                filename = filename.replace(segment, str(w))
            elif key == "pprompt":
                prompt = pnginfo_dict.get("Positive prompt", "").replace("\n", " ")
                if len(parts) >= 2:
                    length = int(parts[1])
                    prompt = prompt[:length]
                filename = filename.replace(segment, prompt.strip())
            elif key == "nprompt":
                prompt = pnginfo_dict.get("Negative prompt", "").replace("\n", " ")
                if len(parts) >= 2:
                    length = int(parts[1])
                    prompt = prompt[:length]
                filename = filename.replace(segment, prompt.strip())
            elif key == "model":
                model = pnginfo_dict.get("Model", "")
                model = os.path.splitext(os.path.basename(model))[0]
                if len(parts) >= 2:
                    length = int(parts[1])
                    model = model[:length]
                filename = filename.replace(segment, model)
            elif key == "date":
                now = datetime.now()
                date_table = {
                    "yyyy": now.year,
                    "MM": now.hour,
                    "dd": now.day,
                    "hh": now.hour,
                    "mm": now.minute,
                    "ss": now.second,
                }
                if len(parts) >= 2:
                    date_format = parts[1]
                    for k, v in date_table.items():
                        date_format = date_format.replace(k, str(v).zfill(len(k)))
                    filename = filename.replace(segment, date_format)
                else:
                    date_format = "yyyyMMddhhmmss"
                    for k, v in date_table.items():
                        date_format = date_format.replace(k, str(v).zfill(len(k)))
                    filename = filename.replace(segment, date_format)

        return filename
