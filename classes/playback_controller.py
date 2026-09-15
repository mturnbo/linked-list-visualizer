from classes.animation import OperationFrame


class PlaybackController:
    def __init__(self, frames: list[OperationFrame]) -> None:
        self.frames = list(frames)
        self.current_frame_index = 0 if self.frames else -1
        self.elapsed_in_frame = 0.0
        self.playing = True

    @property
    def current_frame(self) -> OperationFrame | None:
        if self.current_frame_index < 0:
            return None
        return self.frames[self.current_frame_index]

    @property
    def current_progress(self) -> float:
        frame = self.current_frame
        if frame is None:
            return 0.0
        return max(0.0, min(self.elapsed_in_frame / max(frame.duration, 0.01), 1.0))

    def set_frames(self, frames: list[OperationFrame]) -> None:
        self.frames = list(frames)
        self.restart()

    def play(self) -> None:
        if self.frames:
            self.playing = True

    def pause(self) -> None:
        self.playing = False

    def restart(self) -> None:
        self.current_frame_index = 0 if self.frames else -1
        self.elapsed_in_frame = 0.0
        self.playing = bool(self.frames)

    def jump_to_beginning(self) -> None:
        self.current_frame_index = 0 if self.frames else -1
        self.elapsed_in_frame = 0.0
        self.pause()

    def jump_to_end(self) -> None:
        if not self.frames:
            self.current_frame_index = -1
            self.elapsed_in_frame = 0.0
            self.pause()
            return
        self.current_frame_index = len(self.frames) - 1
        self.elapsed_in_frame = self.frames[-1].duration
        self.pause()

    def step_next(self) -> None:
        if not self.frames:
            self.current_frame_index = -1
            self.elapsed_in_frame = 0.0
            self.pause()
            return
        self.current_frame_index = min(self.current_frame_index + 1, len(self.frames) - 1)
        self.elapsed_in_frame = 0.0
        self.pause()

    def step_previous(self) -> None:
        if not self.frames:
            self.current_frame_index = -1
            self.elapsed_in_frame = 0.0
            self.pause()
            return
        self.current_frame_index = max(self.current_frame_index - 1, 0)
        self.elapsed_in_frame = 0.0
        self.pause()

    def advance(self, seconds: float) -> None:
        if not self.playing or not self.frames:
            return

        remaining = max(0.0, seconds)
        while remaining > 0 and self.current_frame is not None:
            frame = self.current_frame
            available = frame.duration - self.elapsed_in_frame
            if remaining < available:
                self.elapsed_in_frame += remaining
                return
            remaining -= max(available, 0.0)
            if self.current_frame_index >= len(self.frames) - 1:
                self.elapsed_in_frame = frame.duration
                self.pause()
                return
            self.current_frame_index += 1
            self.elapsed_in_frame = 0.0
