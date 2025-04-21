"""
The HeatMouse listener class used to retrieve mouse click data points.

Classes
-------
KeyListener
    Generates several event threads used to listen and report data to the main thread.
"""

# %% --- Imports -----------------------------------------------------------------------
import queue

from pynput import mouse


# %% --- Classes -----------------------------------------------------------------------
# %% KeyListener
class KeyListener:
    """
    Generates several event threads used to listen and report data to the main thread.

    Methods
    -------
    get_next_event
        Retrieve the next even from the event queue.
    on_click
        Add mouse event to the event queue.
    run
        Run the mouse listener.
    start
        Start the mouse listener.
    stop
        Stop the mouse listener.
    """

    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self):
        self.event_queue = queue.Queue()
        self.mouse_listener = mouse.Listener(on_click=self.on_click)

    # %% --- Methods -------------------------------------------------------------------
    # %% get_next_event
    def get_next_event(self, timeout: int = None):
        """
        Retrieve the next event from the event queue.

        Arguments
        ---------
        timeout: int
            Time delay before executing the next event retrieval. Defaults to None.

        Returns
        -------
        tuple
            The event data.
        """
        try:
            return self.event_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            return None

    # %% on_click
    def on_click(self, x: int, y: int, button: mouse.Button, pressed: bool):
        """
        Add mouse event to the event queue.

        Arguments
        ---------
        x: int
            The X-position on the screen.
        y: int
            The Y-position on the screen.
        button: mouse.Button
            The button pressed on the mouse.
        pressed: bool
            Validity bit to check if button was pressed.
        """
        if pressed:
            if button == mouse.Button.left:
                button = "LeftClick"
            elif button == mouse.Button.right:
                button = "RightClick"
            elif button == mouse.Button.middle:
                button = "MiddleClick"
            self.event_queue.put((x, y, button))

    # %% run
    def run(self):
        """Run the mouse listener."""
        self.start()
        self.mouse_listener.join()
        self.stop()
        print("Listener stopped")

    # %% start
    def start(self):
        """Start the mouse listener."""
        self.mouse_listener.start()

    # %% stop
    def stop(self):
        """Stop the mouse listener."""
        self.mouse_listener.stop()
