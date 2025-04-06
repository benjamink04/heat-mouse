import queue
import threading

from pynput import keyboard, mouse


class KeyListener:
    def __init__(self):
        self.event_queue = queue.Queue()
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.keyboard_listener = keyboard.Listener(on_release=self.on_release)

    def on_click(self, x, y, button, pressed):
        if pressed:
            if button == mouse.Button.left:
                button = "Left-Click"
            elif button == mouse.Button.right:
                button = "Right-Click"
            elif button == mouse.Button.middle:
                button = "Middle-Click"
            self.event_queue.put((button, x, y))

    def on_release(self, key):
        if key == keyboard.Key.esc:
            return False  # Stop listener

    def start(self):
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop(self):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

    def get_next_event(self, timeout=None):
        try:
            return self.event_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            return None

    def run(self):
        self.start()
        self.keyboard_listener.join()  # Keep the main thread alive until the listener stops
        self.stop()
        print("Listener stopped")


if __name__ == "__main__":
    key_listener = KeyListener()
    event_thread = threading.Thread(target=key_listener.run)

    event_thread.daemon = (
        True  # Allow the main thread to exit even if this thread is running
    )
    event_thread.start()

    try:
        while event_thread.is_alive():
            event = key_listener.get_next_event(timeout=1)
            if event:
                print(f"Button: {event[0]}, Location: {event[1]}, {event[2]}")
    except KeyboardInterrupt:
        print("Stopping the listener...")
        key_listener.stop()
        event_thread.join()  # Ensure the thread is closed
        print("Listener stopped.")
