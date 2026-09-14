# PySide6 GUI Migration Plan

## Goal

Replace the current pygame animation window with a PySide6 desktop GUI while preserving the existing linked-list operation behavior, command-line print mode, shell workflow, and package-backed linked list implementation.

The first deliverable should be a PySide6 version of the existing animation with feature parity. Once the renderer is stable, add interaction and polish in small increments.

## Proposed Branch

Use `feature/pyside6-gui-plan` for the planning work. Future implementation branches can be split from this plan by milestone, such as `feature/pyside6-animation`, `feature/pyside6-controls`, and `feature/pyside6-export`.

## Current State

- `main.py` supports `print` and `animate` display modes.
- `shell.py` records operations and replays them through `LinkedListVisualizer`.
- `classes/visualizer.py` owns frame generation, node layout, pygame drawing, animation timing, and event handling.
- `classes/linked_list.py` owns operation replay against the package-backed linked list adapter.
- Tests mostly verify parsing, list behavior, and terminal string output. The graphical renderer has little direct automated coverage.

## Target Architecture

Separate the animation model from the GUI renderer:

- `classes/animation.py`
  - Owns `NodeState`, `NodeVisual`, `OperationFrame`, frame generation, interpolation helpers, and layout calculations.
  - Contains no pygame or PySide6 imports.
- `classes/visualizer.py`
  - Becomes a compatibility wrapper that launches the selected renderer.
  - Keeps the current public constructor stable for `main.py` and `shell.py`.
- `classes/renderers/pygame_renderer.py`
  - Temporary home for the existing pygame drawing loop during migration.
  - Can be removed after PySide6 reaches parity.
- `classes/renderers/pyside6_renderer.py`
  - Owns the PySide6 app window, `QGraphicsScene`, graphics items, controls, and screenshot export.
- `classes/gui/`
  - Holds reusable Qt widgets such as operation panel, controls bar, operation form, and graphics view.

This keeps linked-list logic, frame planning, and visual rendering independently testable.

## Increment 1: Convert Existing Animation To PySide6

Objective: reproduce the current animation in PySide6 with the same operation replay behavior.

Tasks:

1. Add PySide6 as a dependency with `uv add PySide6`.
2. Extract renderer-neutral dataclasses and frame-building logic from `classes/visualizer.py` into `classes/animation.py`.
3. Add tests for frame generation:
   - append produces an `add` frame with the new node id.
   - prepend inserts at index 0.
   - insert clamps to the correct visual index.
   - remove records the removed node id.
   - replace records the replaced node id and value.
   - reverse reorders node states.
   - sort clears cycle display and orders nodes using the visualizer sort key.
   - cycle records the tail-to-start link for singly lists.
4. Build a PySide6 window with:
   - `QMainWindow` as the application shell.
   - `QGraphicsScene` and `QGraphicsView` for the canvas.
   - `QGraphicsEllipseItem` or custom node items for nodes.
   - `QGraphicsPathItem` for singly, doubly, wrapped-row, and cycle arrows.
   - `QTimer` or `QTimeLine` for frame progression.
5. Add a new display mode while keeping pygame available during transition:
   - `print`
   - `animate`
   - `gui`
6. Wire `main.py` and `shell.py` so `gui` launches the PySide6 renderer.
7. Verify with:
   - `uv run pytest`
   - `uv run python main.py singly gui --ops-file examples/ops1.txt`
   - `uv run python main.py doubly gui --values 1,2,3,4,5`

Acceptance criteria:

- Existing command-line and shell workflows still work.
- PySide6 displays append, prepend, insert, remove, replace, reverse, sort, cycle, and has-cycle frames.
- Current pygame behavior remains available until the PySide6 renderer is accepted.

## Increment 2: Better Node Styling

Objective: make the visualization feel like a polished educational desktop app.

Tasks:

1. Replace plain circles with custom node graphics items.
2. Add distinct visual states:
   - normal
   - newly added
   - recently changed
   - removing
   - selected/current
   - cycle endpoint
3. Use a restrained color palette with strong contrast on a neutral canvas.
4. Render each value inside a rounded node body with consistent padding.
5. Add arrow styling:
   - clean arrowheads
   - curved cycle links
   - subtle reverse arrows for doubly lists
   - row-wrap connectors with clear bends.
6. Add theme constants for colors, fonts, radii, stroke widths, and spacing.

Acceptance criteria:

- Values remain readable for common integers, floats, booleans, and short strings.
- Empty, one-node, multi-row, and cycle layouts look intentional.
- Styling can be changed without editing animation logic.

## Increment 3: Operations Input

Objective: let users build and modify a linked list directly from the GUI.

Tasks:

1. Add an operations panel with:
   - list type selector.
   - value input.
   - index input where needed.
   - operation selector or dedicated buttons.
   - sort method selector.
2. Support append, prepend, insert, remove, replace, reverse, sort, cycle, has-cycle, and clear.
3. Validate operation inputs before adding them to the animation queue.
4. Reuse existing parsing and value coercion rules from `utils.py`.
5. Show operation history with current operation highlighting.
6. Add load-from-file support for existing operation files.
7. Add reset/replay behavior after editing the operation queue.

Acceptance criteria:

- A user can build the same animations from the GUI that they can currently build from `--values` or `--ops-file`.
- Invalid inputs produce inline errors without crashing the app.
- Operation history remains synchronized with the scene.

## Increment 4: Play, Pause, And Step Controls

Objective: give users precise control over animation playback.

Tasks:

1. Add toolbar controls:
   - play
   - pause
   - restart
   - previous frame
   - next frame
   - jump to beginning
   - jump to end.
2. Move playback state into a controller class.
3. Track:
   - current frame index.
   - elapsed time in the current frame.
   - playing/paused state.
4. Allow stepping while paused.
5. Keep operation panel highlighting in sync.

Acceptance criteria:

- Playback can be paused and resumed without losing frame progress.
- Step controls work deterministically.
- Restart always returns to the first frame.

## Increment 5: Speed Slider

Objective: make animation timing adjustable without rebuilding the operation list.

Tasks:

1. Add a slider for playback speed, such as 0.25x to 4x.
2. Scale frame duration and arrow animation duration through the playback controller.
3. Display the current speed beside the slider.
4. Preserve speed when replaying, stepping, or loading a new operation file.

Acceptance criteria:

- Speed changes apply immediately during playback.
- Very slow and very fast speeds remain usable.
- Tests cover controller duration calculations.

## Increment 6: Zoom And Pan

Objective: support larger linked lists and multi-row layouts comfortably.

Tasks:

1. Subclass `QGraphicsView` for canvas interactions.
2. Add mouse-wheel zoom centered on cursor.
3. Add click-drag panning.
4. Add fit-to-view and reset-zoom buttons.
5. Define min and max zoom levels.
6. Keep the operations panel fixed while only the canvas pans/zooms.

Acceptance criteria:

- Large lists can be inspected without overlapping the operation panel.
- Zoom and pan do not change node layout state.
- Fit-to-view frames the current list cleanly.

## Increment 7: Export Screenshot

Objective: let users save the current visualization as an image.

Tasks:

1. Add an export button to the toolbar.
2. Use `QFileDialog` to choose a destination path.
3. Render the current `QGraphicsScene` to a `QImage` or `QPixmap`.
4. Support PNG by default.
5. Include only the graph canvas by default, with an optional full-window export later.
6. Add success and failure status messages.

Acceptance criteria:

- Exported PNG matches the currently visible linked-list state.
- Export works when paused, after stepping, and at the end of playback.
- Export failures are surfaced without crashing.

## Testing Strategy

Prioritize deterministic tests below the GUI event loop:

- Unit-test frame generation in `classes/animation.py`.
- Unit-test playback controller transitions.
- Unit-test operation validation and queue mutation.
- Smoke-test PySide6 imports behind optional skips when Qt is unavailable.
- Add a manual QA checklist for rendering behavior until automated Qt screenshot tests are introduced.

Manual QA checklist:

- Singly append/prepend/insert/remove/replace/reverse/sort/cycle.
- Doubly append/prepend/insert/remove/replace/reverse/sort.
- Empty list.
- One-node list.
- Long list with row wrapping.
- Mixed values: integers, floats, booleans, and strings.
- Pause, resume, step forward, step back, speed changes.
- Zoom, pan, fit-to-view, reset zoom.
- Screenshot export.

## Dependency Plan

Initial dependency set:

- Keep `mt-linked-list`.
- Add `PySide6`.
- Keep `pygame` during the transition.
- Remove `pygame` only after PySide6 reaches feature parity and the old renderer is retired.

## Suggested Commit Sequence

1. `test: cover renderer independent animation frames`
2. `refactor: extract animation frame model`
3. `feat: add pyside6 animation renderer`
4. `feat: add gui operation input`
5. `feat: add playback controls`
6. `feat: add animation speed control`
7. `feat: add canvas zoom and pan`
8. `feat: export visualization screenshots`
9. `chore: retire pygame renderer`

## Open Decisions

- Whether `animate` should eventually mean PySide6, or whether `gui` should remain the permanent display mode.
- Whether screenshots should export the canvas only or the full application window.
- Whether operation history should be editable in place or rebuilt through reset and replay.
- Whether a future release should package this as a desktop app.
