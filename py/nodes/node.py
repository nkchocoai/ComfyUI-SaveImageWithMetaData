import json
import os
import re

from datetime import datetime

from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np

import piexif
import piexif.helper

import folder_paths
from comfy.cli_args import args

from .base import BaseNode

from ..capture import Capture
from .. import hook
from ..trace import Trace

from ..defs.combo import SAMPLER_SELECTION_METHOD


# refer. https://github.com/comfyanonymous/ComfyUI/blob/38b7ac6e269e6ecc5bdd6fefdfb2fb1185b09c9d/nodes.py#L1411
class SaveImageWithMetaData(BaseNode):
    SAVE_FILE_FORMATS = ["png", "jpeg", "webp"]

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
                "file_format": (s.SAVE_FILE_FORMATS,),
            },
            "optional": {
                "lossless_webp": ("BOOLEAN", {"default": True}),
                "quality": ("INT", {"default": 100, "min": 1, "max": 100}),
                "save_workflow_json": ("BOOLEAN", {"default": False}),
                "add_counter_to_filename": ("BOOLEAN", {"default": True}),
                "civitai_sampler": ("BOOLEAN", {"default": False}),
                "extra_metadata": ("EXTRA_METADATA", {}),
                "save_workflow_image": ("BOOLEAN", {"default": True}),
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
        file_format="png",
        lossless_webp=True,
        quality=100,
        save_workflow_json=False,
        add_counter_to_filename=True,
        civitai_sampler=False,
        extra_metadata={},
        prompt=None,
        extra_pnginfo=None,
        save_workflow_image=True,
    ):
        pnginfo_dict_src = self.gen_pnginfo(
            sampler_selection_method, sampler_selection_node_id, civitai_sampler
        )
        for k, v in extra_metadata.items():
            if k and v:
                pnginfo_dict_src[k] = v.replace(",", "/")

        results = list()
        for index, image in enumerate(images):
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            pnginfo_dict = pnginfo_dict_src.copy()
            if len(images) >= 2:
                pnginfo_dict["Batch index"] = index
                pnginfo_dict["Batch size"] = len(images)

            metadata = None
            parameters = ""
            if not args.disable_metadata:
                metadata = PngInfo()
                parameters = Capture.gen_parameters_str(pnginfo_dict)
                if pnginfo_dict:
                    metadata.add_text("parameters", parameters)
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                if save_workflow_image == False:
                    metadata.add_text("workflow", "")
            
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
            base_filename = filename
            if add_counter_to_filename:
                base_filename += f"_{counter:05}_"
            file = base_filename + "." + file_format
            file_path = os.path.join(full_output_folder, file)

            if file_format == "png":
                img.save(
                    file_path,
                    pnginfo=metadata,
                    compress_level=self.compress_level,
                )
            else:
                img.save(
                    file_path,
                    optimize=True,
                    quality=quality,
                    lossless=lossless_webp,
                )
                exif_bytes = piexif.dump(
                    {
                        "Exif": {
                            piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(
                                parameters, encoding="unicode"
                            ),
                        },
                    }
                )
                piexif.insert(exif_bytes, file_path)

            if save_workflow_json:
                file_path_workflow = os.path.join(
                    full_output_folder, f"{base_filename}.json"
                )
                with open(file_path_workflow, "w", encoding="utf-8") as f:
                    json.dump(extra_pnginfo["workflow"], f)

            results.append(
                {"filename": file, "subfolder": subfolder, "type": self.type}
            )
            counter += 1

        return {"ui": {"images": results}}

    @classmethod
    def gen_pnginfo(
        cls, sampler_selection_method, sampler_selection_node_id, save_civitai_sampler
    ):
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
            inputs_before_sampler_node, inputs_before_this_node, save_civitai_sampler
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
                    "MM": now.month,
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


class CreateExtraMetaData(BaseNode):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key1": ("STRING", {"default": "", "multiline": False}),
                "value1": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "key2": ("STRING", {"default": "", "multiline": False}),
                "value2": ("STRING", {"default": "", "multiline": False}),
                "key3": ("STRING", {"default": "", "multiline": False}),
                "value3": ("STRING", {"default": "", "multiline": False}),
                "key4": ("STRING", {"default": "", "multiline": False}),
                "value4": ("STRING", {"default": "", "multiline": False}),
                "extra_metadata": ("EXTRA_METADATA",),
            },
        }

    RETURN_TYPES = ("EXTRA_METADATA",)
    FUNCTION = "create_extra_metadata"

    def create_extra_metadata(
        self,
        extra_metadata={},
        key1="",
        value1="",
        key2="",
        value2="",
        key3="",
        value3="",
        key4="",
        value4="",
    ):
        extra_metadata.update(
            {
                key1: value1,
                key2: value2,
                key3: value3,
                key4: value4,
            }
        )
        return (extra_metadata,)
