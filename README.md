# ComfyUI-SaveImageWithMetaData
![SaveImageWithMetaData Preview](img/save_image_with_metadata.png)  
日本語版READMEは[こちら](README.jp.md)。

- Custom node for [ComfyUI](https://github.com/comfyanonymous/ComfyUI).
- Add a node to save images with metadata (PNGInfo) extracted from the input values of each node.
- Since the values are extracted dynamically, values output by various extension nodes can be added to metadata.

## Installation
```
cd <ComfyUI directory>/custom_nodes
git clone https://github.com/nkchocoai/ComfyUI-SaveImageWithMetaData.git
```

## Nodes
### Save Image With Metadata
- Saves the `images` received as input as an image with metadata (PNGInfo).
- Metadata is extracted from the input of the KSampler node found by `sampler_selection_method` and the input of the previously executed node.
  - Target KSampler nodes are the key of `SAMPLERS` in the file [py/defs/samplers.py](py/defs/samplers.py) and the file in [py/defs/ext/](py/defs/ext/).

#### filename_prefix
- The string (Key) specified in `filename_prefix` will be replaced with the retrieved information.

| Key             | Information to be replaced            |
| --------------- | ------------------------------------- |
| %seed%          | seed value                            |
| %width%         | Image width                           |
| %height%        | Image height                          |
| %pprompt%       | Positive Prompt                       |
| %pprompt:[n]%   | first n characters of Positive Prompt |
| %nprompt%       | Negative Prompt                       |
| %nprompt:[n]%   | First n characters of Negative Prompt |
| %model%         | Checkpoint name                       |
| %model:[n]%     | First n characters of Checkpoint name |
| %date%          | Date of generation(yyyyMMddhhmmss)    |
| %date:[format]% | Date of generation                    |

- See the following table for the identifier specified by `[format]` in `%date:[format]%`.

| Identifier | Description |
| ---------- | ----------- |
| yyyy       | year        |
| MM         | month       |
| dd         | day         |
| hh         | hour        |
| mm         | minute      |
| ss         | second      |

#### sampler_selection_method
- Specifies how to select a KSampler node that has been executed before this node.

##### Farthest
- Selects the farthest KSampler node from this node.
- Example: In [everywhere_prompt_utilities.png](examples/everywhere_prompt_utilities.png), select the upper KSampler node (seed=12345).

##### Nearest
- Select the nearest KSampler node to this node.
- Example: In [everywhere_prompt_utilities.png](examples/everywhere_prompt_utilities.png), select the bottom KSampler node (seed=67890).

##### By node ID
- Select the KSampler node whose node ID is `sampler_selection_node_id`.

### Create Extra MetaData
- Specifies metadata to be added to the image to be saved.
- Example: In [extra_metadata.png](examples/extra_metadata.png).

## Metadata to be given
- Positive prompt
- Negative prompt
- Steps
- Sampler
- CFG Scale
- Seed
- Clip skip
- Size
- Model
- Model hash
- VAE
  - It is referenced from the input of SaveImageWithMetadata node, not KSampler node.
- VAE hash
  - It is referenced from the input of SaveImageWithMetadata node, not KSampler node.
- Loras
  - Model name
  - Model hash
  - Strength model
  - Strength clip
- Embeddings
  - Name
  - Hash
- If batch size >= 2 :
  - Batch index
  - Batch size
- Hashes
  - Model, Loras, Embeddings
  - For [Civitai](https://civitai.com/)

## Supported nodes and extensions
- Please check the following file for supported nodes.
  - [py/defs/captures.py](py/defs/captures.py)
  - [py/defs/samplers.py](py/defs/samplers.py)
- Please check the following directories for supported extensions.
  - [py/defs/ext/](py/defs/ext/)
