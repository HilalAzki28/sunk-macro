import threading
import time
from pynput import mouse, keyboard
from src.utils import deserialize_key, deserialize_button

class ActionPlayer:
    def __init__(self, on_event_played=None, on_status_change=None):
        self.on_event_played = on_event_played
        self.on_status_change = on_status_change
        
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        
        self.stop_event = threading.Event()
        self.play_thread = None
        self.is_playing = False
        
        # Playback configuration
        self.speed_factor = 1.0
        self.loop_count = 1  # 1 = run once, <= 0 or None = infinite
        self.loop_delay = 0.0

    def start(self, events):
        if self.is_playing:
            return
        if not events:
            return
            
        self.stop_event.clear()
        self.is_playing = True
        self.play_thread = threading.Thread(target=self._run_playback, args=(events,), daemon=True)
        self.play_thread.start()

    def stop(self):
        if not self.is_playing:
            return
        self.stop_event.set()
        self.is_playing = False
        if self.play_thread:
            self.play_thread.join(timeout=1.0)
            self.play_thread = None
        if self.on_status_change:
            self.on_status_change("Idle")

    def _run_playback(self, events):
        if self.on_status_change:
            self.on_status_change("Playing")
            
        loop = 0
        infinite = self.loop_count <= 0
        
        # Track pressed keys/buttons to release them upon stopping (prevents stuck states)
        pressed_keys = set()
        pressed_buttons = set()
        
        try:
            while not self.stop_event.is_set():
                # Loop control
                if not infinite and loop >= self.loop_count:
                    break
                
                # Wait between loops
                if loop > 0 and self.loop_delay > 0:
                    if self.stop_event.wait(self.loop_delay):
                        break
                
                prev_time = 0.0
                for event in events:
                    if self.stop_event.is_set():
                        break
                        
                    # Calculate wait time between actions
                    current_time = event['time']
                    delay = (current_time - prev_time) / self.speed_factor
                    prev_time = current_time
                    
                    if delay > 0:
                        # Interruptible sleep
                        if self.stop_event.wait(delay):
                            break
                            
                    # Execute event
                    try:
                        self._execute_event(event, pressed_keys, pressed_buttons)
                    except Exception as e:
                        print(f"Error executing event: {e}")
                        
                    if self.on_event_played:
                        self.on_event_played(event)
                
                loop += 1
        finally:
            # Cleanup stuck inputs
            for key in list(pressed_keys):
                try:
                    self.keyboard_controller.release(key)
                except Exception:
                    pass
            for button in list(pressed_buttons):
                try:
                    self.mouse_controller.release(button)
                except Exception:
                    pass
                    
            self.is_playing = False
            if self.on_status_change:
                self.on_status_change("Idle")

    def _execute_event(self, event, pressed_keys, pressed_buttons):
        etype = event['type']
        
        if etype == 'mouse_click':
            # Position mouse before click
            self.mouse_controller.position = (event['x'], event['y'])
            button = deserialize_button(event['button'])
            if button:
                if event['pressed']:
                    self.mouse_controller.press(button)
                    pressed_buttons.add(button)
                else:
                    self.mouse_controller.release(button)
                    pressed_buttons.discard(button)
            
        elif etype == 'key_press':
            key = deserialize_key(event['key'])
            if key:
                self.keyboard_controller.press(key)
                pressed_keys.add(key)
                
        elif etype == 'key_release':
            key = deserialize_key(event['key'])
            if key:
                self.keyboard_controller.release(key)
                pressed_keys.discard(key)
