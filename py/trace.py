from collections import deque

from .defs.samplers import SAMPLERS
from .defs.combo import SAMPLER_SELECTION_METHOD


class Trace:
    @classmethod
    def trace(cls, start_node_id, prompt):
        class_type = prompt[start_node_id]["class_type"]
        Q = deque()
        Q.append((start_node_id, 0))
        trace_tree = {start_node_id: (0, class_type)}
        while len(Q) > 0:
            current_node_id, distance = Q.popleft()
            input_fields = prompt[current_node_id]["inputs"]
            for value in input_fields.values():
                if isinstance(value, list):
                    nid = value[0]
                    class_type = prompt[nid]["class_type"]
                    trace_tree[nid] = (distance + 1, class_type)
                    Q.append((nid, distance + 1))
        return trace_tree

    @classmethod
    def find_sampler_node_id(cls, trace_tree, sampler_selection_method, node_id):
        if sampler_selection_method == SAMPLER_SELECTION_METHOD[2]:
            node_id = str(node_id)
            _, class_type = trace_tree.get(node_id, (-1, None))
            if class_type in SAMPLERS.keys():
                return node_id
            return -1

        sorted_by_distance_trace_tree = sorted(
            [(k, v[0], v[1]) for k, v in trace_tree.items()],
            key=lambda x: x[1],
            reverse=(sampler_selection_method == SAMPLER_SELECTION_METHOD[0]),
        )
        for nid, _, class_type in sorted_by_distance_trace_tree:
            if class_type in SAMPLERS.keys():
                return nid
        return -1

    @classmethod
    def filter_inputs_by_trace_tree(cls, inputs, trace_tree):
        filtered_inputs = {}
        for meta, inputs_list in inputs.items():
            for node_id, input_value in inputs_list:
                trace = trace_tree.get(node_id)
                if trace is not None:
                    distance = trace[0]
                    if meta not in filtered_inputs:
                        filtered_inputs[meta] = []
                    filtered_inputs[meta].append((node_id, input_value, distance))

        # sort by distance
        for k, v in filtered_inputs.items():
            filtered_inputs[k] = sorted(v, key=lambda x: x[2])
        return filtered_inputs
