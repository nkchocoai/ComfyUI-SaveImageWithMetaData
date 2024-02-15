import json

from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np

import folder_paths
from comfy.cli_args import args

from .base import BaseNode
from .. import hook
from ..defs.hooks import hooks
from ..defs.samplers import samplers
from ..defs.meta import MetaField

from nodes import NODE_CLASS_MAPPINGS
from execution import get_input_data


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
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    def save_images(
        self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None
    ):
        (
            full_output_folder,
            filename,
            counter,
            subfolder,
            filename_prefix,
        ) = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
        )
        results = list()
        print("Save Image With Metadata")
        for image in images:
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                # metadata.add_text("parameters", comment)
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            file = f"{filename}_{counter:05}_.png"
            # img.save(
            #     os.path.join(full_output_folder, file),
            #     pnginfo=metadata,
            #     compress_level=self.compress_level,
            # )
            inputs = self.get_inputs()
            print("[get_inputs]")
            print(inputs)
            pnginfo_dict = self.gen_pnginfo_dict(inputs)
            print("[PNGInfo Dict]")
            print(pnginfo_dict)
            results.append(
                {"filename": file, "subfolder": subfolder, "type": self.type}
            )
            counter += 1

        return {"ui": {"images": results}}

    def get_inputs(self):
        inputs = {}
        prompt = hook.current_prompt
        extra_data = hook.current_extra_data
        outputs = hook.prompt_executer.outputs

        for node_id, obj in prompt.items():
            class_type = obj["class_type"]
            obj_class = NODE_CLASS_MAPPINGS[class_type]
            node_inputs = prompt[node_id]["inputs"]
            input_data_all = get_input_data(
                node_inputs, obj_class, node_id, outputs, prompt, extra_data
            )
            for node_class, metas in hooks.items():
                if class_type == node_class:
                    for meta, field_data in metas.items():
                        validate = field_data.get("validate")
                        if validate is not None and not validate(
                            node_id, obj, prompt, extra_data, outputs, input_data_all
                        ):
                            print("validate failed", meta, node_id, obj)
                            continue

                        if meta not in inputs:
                            inputs[meta] = []
                        field_name = field_data["field_name"]
                        value = input_data_all.get(field_name)
                        if value is not None:
                            format = field_data.get("format")
                            v = value
                            if format is not None:
                                v = format(v)
                            if isinstance(value, list) and len(value) > 0:
                                v = value[0]
                            inputs[meta].append((node_id, v))
        return inputs

    def gen_pnginfo_dict(self, inputs):
        pnginfo_dict = {}

        def update_pnginfo_dict(metafield, key):
            x = inputs.get(metafield, [])
            if len(x) > 0:
                pnginfo_dict[key] = x[-1][1]

        update_pnginfo_dict(MetaField.POSITIVE_PROMPT, "")
        update_pnginfo_dict(MetaField.NEGATIVE_PROMPT, "Negative prompt")
        update_pnginfo_dict(MetaField.STEPS, "Steps")

        sampler_names = inputs.get(MetaField.SAMPLER_NAME, [])
        if len(sampler_names) > 0:
            pnginfo_dict["Sampler"] = sampler_names[0][1]

            schedulers = inputs.get(MetaField.SCHEDULER, [])
            if len(schedulers) > 0:
                scheduler = schedulers[0][1]
                if scheduler != "normal":
                    pnginfo_dict["Sampler"] += "_" + scheduler

        update_pnginfo_dict(MetaField.CFG, "CFG Scale")
        update_pnginfo_dict(MetaField.SEED, "Seed")

        image_widths = inputs.get(MetaField.IMAGE_WIDTH, [])
        image_heights = inputs.get(MetaField.IMAGE_HEIGHT, [])
        if len(image_widths) > 0 and len(image_heights) > 0:
            pnginfo_dict["Size"] = f"{image_widths[0][1]}x{image_heights[0][1]}"

        return pnginfo_dict
