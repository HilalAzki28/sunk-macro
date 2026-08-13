import time
from pynput import mouse, keyboard
from src.utils import serialize_event

class ActionRecorder:
    def __init__(self, on_event_callback=None, ignore_keys=None):
        self.on_event_callback = on_event_callback
        self.ignore_keys = ignore_keys or set()
        self.events = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.is_recording = False
        
        # Recording filters configuration
        self.record_mouse_click = True
        self.record_keyboard = True

    def get_elapsed_time(self):
        if self.start_time is None:
            return 0.0
        return time.perf_counter() - self.start_time

    def _add_event(self, event):
        self.events.append(event)
        if self.on_event_callback:
            self.on_event_callback(event)

    def on_click(self, x, y, button, pressed):
        if not self.is_recording or not self.record_mouse_click:
            return
        event = serialize_event('mouse_click', self.get_elapsed_time(), x=x, y=y, button=button, pressed=pressed)
        self._add_event(event)

    def on_press(self, key):
        if not self.is_recording or not self.record_keyboard:
            return
        # Skip ignore keys (like F8/F9 hotkeys)
        if key in self.ignore_keys:
            return
        event = serialize_event('key_press', self.get_elapsed_time(), key=key)
        self._add_event(event)

    def on_release(self, key):
        if not self.is_recording or not self.record_keyboard:
            return
        # Skip ignore keys
        if key in self.ignore_keys:
            return
        event = serialize_event('key_release', self.get_elapsed_time(), key=key)
        self._add_event(event)

    def start(self):
        if self.is_recording:
            return
        self.events = []
        self.start_time = time.perf_counter()
        self.is_recording = True

        # Start background listeners
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def stop(self):
        if not self.is_recording:
            return []
        self.is_recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            
        return self.events
