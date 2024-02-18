import json
import os

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
            input_data = get_input_data(
                node_inputs, obj_class, node_id, outputs, prompt, extra_data
            )
            for node_class, metas in CAPTURE_FIELD_LIST.items():
                if class_type == node_class:
                    for meta, field_data in metas.items():
                        validate = field_data.get("validate")
                        if validate is not None and not validate(
                            node_id, obj, prompt, extra_data, outputs, input_data
                        ):
                            continue

                        if meta not in inputs:
                            inputs[meta] = []

                        value = field_data.get("value")
                        if value is not None:
                            inputs[meta].append((node_id, value))
                            continue

                        field_name = field_data["field_name"]
                        value = input_data.get(field_name)
                        if value is not None:
                            format = field_data.get("format")
                            v = value
                            if isinstance(value, list) and len(value) > 0:
                                v = value[0]
                            if format is not None:
                                v = format(v, input_data)
                            if isinstance(v, list):
                                for x in v:
                                    inputs[meta].append((node_id, x))
                            else:
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

        update_pnginfo_dict(MetaField.CLIP_SKIP, "Clip skip")

        image_widths = inputs.get(MetaField.IMAGE_WIDTH, [])
        image_heights = inputs.get(MetaField.IMAGE_HEIGHT, [])
        if len(image_widths) > 0 and len(image_heights) > 0:
            pnginfo_dict["Size"] = f"{image_widths[0][1]}x{image_heights[0][1]}"

        update_pnginfo_dict(MetaField.MODEL_NAME, "Model")
        update_pnginfo_dict(MetaField.MODEL_HASH, "Model hash")

        pnginfo_dict.update(cls.gen_loras(inputs))
        pnginfo_dict.update(cls.gen_embeddings(inputs))

        hashes_for_civitai = cls.get_hashes_for_civitai(inputs)
        if len(hashes_for_civitai) > 0:
            pnginfo_dict["Hashes"] = json.dumps(hashes_for_civitai)

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

    @classmethod
    def get_hashes_for_civitai(cls, inputs):
        resource_hashes = {}
        model_hashes = inputs.get(MetaField.MODEL_HASH, [])
        if len(model_hashes) > 0:
            resource_hashes["model"] = model_hashes[0][1]

        lora_model_names = inputs.get(MetaField.LORA_MODEL_NAME, [])
        lora_model_hashes = inputs.get(MetaField.LORA_MODEL_HASH, [])
        for lora_model_name, lora_model_hash in zip(
            lora_model_names, lora_model_hashes
        ):
            lora_model_name = os.path.splitext(os.path.basename(lora_model_name[1]))[0]
            resource_hashes[f"lora:{lora_model_name}"] = lora_model_hash[1]

        embedding_names = inputs.get(MetaField.EMBEDDING_NAME, [])
        embedding_hashes = inputs.get(MetaField.EMBEDDING_HASH, [])
        for embedding_name, embedding_hash in zip(embedding_names, embedding_hashes):
            embedding_name = os.path.splitext(os.path.basename(embedding_name[1]))[0]
            resource_hashes[f"embed:{embedding_name}"] = embedding_hash[1]

        return resource_hashes

    @classmethod
    def gen_loras(cls, inputs):
        pnginfo_dict = {}

        model_names = inputs.get(MetaField.LORA_MODEL_NAME, [])
        model_hashes = inputs.get(MetaField.LORA_MODEL_HASH, [])
        strength_models = inputs.get(MetaField.LORA_STRENGTH_MODEL, [])
        strength_clips = inputs.get(MetaField.LORA_STRENGTH_CLIP, [])

        index = 0
        for model_name, model_hashe, strength_model, strength_clip in zip(
            model_names, model_hashes, strength_models, strength_clips
        ):
            field_prefix = f"Lora_{index}"
            pnginfo_dict[f"{field_prefix} Model name"] = os.path.basename(model_name[1])
            pnginfo_dict[f"{field_prefix} Model hash"] = model_hashe[1]
            pnginfo_dict[f"{field_prefix} Strength model"] = strength_model[1]
            pnginfo_dict[f"{field_prefix} Strength clip"] = strength_clip[1]
            index += 1

        return pnginfo_dict

    @classmethod
    def gen_embeddings(cls, inputs):
        pnginfo_dict = {}

        embedding_names = inputs.get(MetaField.EMBEDDING_NAME, [])
        embedding_hashes = inputs.get(MetaField.EMBEDDING_HASH, [])

        index = 0
        for embedding_name, embedding_hashe in zip(embedding_names, embedding_hashes):
            field_prefix = f"Embedding_{index}"
            pnginfo_dict[f"{field_prefix} name"] = os.path.basename(embedding_name[1])
            pnginfo_dict[f"{field_prefix} hash"] = embedding_hashe[1]
            index += 1

        return pnginfo_dict
