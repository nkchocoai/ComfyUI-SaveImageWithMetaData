from . import hook
from .defs.captures import CAPTURE_FIELD_LIST
from .defs.meta import MetaField

from nodes import NODE_CLASS_MAPPINGS
from execution import get_input_data


class Capture:
    @classmethod
    def get_inputs(cls):
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
            for node_class, metas in CAPTURE_FIELD_LIST.items():
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
                            if isinstance(value, list) and len(value) > 0:
                                v = value[0]
                            if format is not None:
                                v = format(v)
                            inputs[meta].append((node_id, v))
        return inputs

    @classmethod
    def gen_pnginfo_dict(cls, inputs):
        pnginfo_dict = {}

        def update_pnginfo_dict(metafield, key):
            x = inputs.get(metafield, [])
            if len(x) > 0:
                pnginfo_dict[key] = x[0][1]

        update_pnginfo_dict(MetaField.POSITIVE_PROMPT, "Positive prompt")
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

        update_pnginfo_dict(MetaField.MODEL_NAME, "Model name")
        update_pnginfo_dict(MetaField.MODEL_HASH, "Model hash")

        return pnginfo_dict

    @classmethod
    def gen_parameters_str(cls, pnginfo_dict):
        result = pnginfo_dict.get("Positive prompt", "") + "\n"
        result += "Negative prompt: " + pnginfo_dict.get("Negative prompt", "") + "\n"

        s_list = []
        pnginfo_dict_without_prompt = {
            k: v
            for k, v in pnginfo_dict.items()
            if k not in {"Positive prompt", "Negative prompt"}
        }
        for k, v in pnginfo_dict_without_prompt.items():
            s = str(v).strip().replace("\n", " ")
            s_list.append(f"{k}: {s}")

        return result + ", ".join(s_list)
