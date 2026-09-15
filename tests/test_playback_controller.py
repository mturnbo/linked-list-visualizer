from classes.animation import OperationFrame
from classes.playback_controller import PlaybackController


def test_playback_controller_advances_within_current_frame():
    controller = PlaybackController([OperationFrame("add", 2.0, [], [])])

    controller.advance(0.5)

    assert controller.current_frame_index == 0
    assert controller.elapsed_in_frame == 0.5
    assert controller.current_progress == 0.25


def test_playback_controller_pauses_without_losing_progress():
    controller = PlaybackController([OperationFrame("add", 2.0, [], [])])
    controller.advance(0.5)

    controller.pause()
    controller.advance(0.5)
    controller.play()
    controller.advance(0.25)

    assert controller.current_frame_index == 0
    assert controller.elapsed_in_frame == 0.75


def test_playback_controller_steps_while_paused():
    frames = [
        OperationFrame("add", 1.0, [], []),
        OperationFrame("remove", 1.0, [], []),
        OperationFrame("replace", 1.0, [], []),
    ]
    controller = PlaybackController(frames)

    controller.pause()
    controller.step_next()
    controller.step_next()
    controller.step_previous()

    assert controller.current_frame_index == 1
    assert controller.elapsed_in_frame == 0.0
    assert not controller.playing


def test_playback_controller_jumps_to_boundaries():
    frames = [
        OperationFrame("add", 1.0, [], []),
        OperationFrame("remove", 2.0, [], []),
    ]
    controller = PlaybackController(frames)

    controller.jump_to_end()
    assert controller.current_frame_index == 1
    assert controller.elapsed_in_frame == 2.0
    assert controller.current_progress == 1.0

    controller.jump_to_beginning()
    assert controller.current_frame_index == 0
    assert controller.elapsed_in_frame == 0.0
    assert controller.current_progress == 0.0


def test_playback_controller_restart_returns_to_first_frame_and_plays():
    controller = PlaybackController(
        [
            OperationFrame("add", 1.0, [], []),
            OperationFrame("remove", 1.0, [], []),
        ]
    )
    controller.jump_to_end()

    controller.restart()

    assert controller.current_frame_index == 0
    assert controller.elapsed_in_frame == 0.0
    assert controller.playing


def test_playback_controller_handles_empty_frame_list():
    controller = PlaybackController([])

    controller.advance(1.0)
    controller.step_next()
    controller.jump_to_end()

    assert controller.current_frame is None
    assert controller.current_frame_index == -1
    assert controller.elapsed_in_frame == 0.0
    assert controller.current_progress == 0.0
