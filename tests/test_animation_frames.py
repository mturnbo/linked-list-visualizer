from classes.visualizer import LinkedListVisualizer


def build_frames(ll_type, operations):
    visualizer = LinkedListVisualizer(ll_type, operations)
    return visualizer.build_frames(operations, interval=0.25)


def values(nodes):
    return [node.value for node in nodes]


def test_append_produces_add_frame_with_new_node_id():
    frames = build_frames("singly", [("append", [1], "append 1")])

    assert frames[0].op_type == "add"
    assert frames[0].added_id == 0
    assert frames[0].current_new_id == 0
    assert values(frames[0].nodes_after) == [1]


def test_prepend_inserts_at_visual_index_zero():
    frames = build_frames(
        "singly",
        [
            ("append", [2], "append 2"),
            ("prepend", [1], "prepend 1"),
        ],
    )

    assert frames[-1].op_type == "add"
    assert values(frames[-1].nodes_after) == [1, 2]
    assert frames[-1].nodes_after[0].node_id == frames[-1].added_id


def test_insert_clamps_to_visual_index():
    frames = build_frames(
        "singly",
        [
            ("append", [1], "append 1"),
            ("insert", [99, 2], "insert beyond end"),
            ("insert", [-4, 0], "insert before start"),
        ],
    )

    assert values(frames[1].nodes_after) == [1, 2]
    assert frames[1].nodes_after[-1].node_id == frames[1].added_id
    assert values(frames[2].nodes_after) == [0, 1, 2]
    assert frames[2].nodes_after[0].node_id == frames[2].added_id


def test_remove_records_removed_node_id():
    frames = build_frames(
        "singly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
            ("append", [3], "append 3"),
            ("remove", [1], "remove middle"),
        ],
    )

    assert frames[-1].op_type == "remove"
    assert frames[-1].removed_id == 1
    assert values(frames[-1].nodes_after) == [1, 3]


def test_replace_records_replaced_node_id_and_value():
    frames = build_frames(
        "doubly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
            ("replace", [1, 9], "replace second"),
        ],
    )

    assert frames[-1].op_type == "replace"
    assert frames[-1].replaced_id == 1
    assert values(frames[-1].nodes_after) == [1, 9]


def test_reverse_reorders_node_states():
    frames = build_frames(
        "singly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
            ("append", [3], "append 3"),
            ("reverse", [], "reverse"),
        ],
    )

    assert frames[-1].op_type == "reverse"
    assert values(frames[-1].nodes_after) == [3, 2, 1]
    assert [node.node_id for node in frames[-1].nodes_after] == [2, 1, 0]


def test_sort_orders_nodes_by_visual_sort_key():
    frames = build_frames(
        "singly",
        [
            ("append", ["b"], "append b"),
            ("append", ["a"], "append a"),
            ("append", [2], "append 2"),
            ("sort", [1], "sort"),
        ],
    )

    assert frames[-1].op_type == "sort"
    assert values(frames[-1].nodes_after) == [2, "a", "b"]
    assert frames[-1].cycle_link is None


def test_cycle_records_tail_to_start_link_for_singly_lists():
    frames = build_frames(
        "singly",
        [
            ("append", [1], "append 1"),
            ("append", [2], "append 2"),
            ("append", [3], "append 3"),
            ("cycle", [0], "cycle"),
        ],
    )

    assert frames[-1].op_type == "cycle"
    assert frames[-1].cycle_link == (2, 0)
