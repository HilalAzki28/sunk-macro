import json
from pynput import keyboard, mouse

def serialize_key(key):
    """Converts a pynput key event to a JSON-serializable dictionary."""
    if key is None:
        return None
    if hasattr(key, 'name') and key.name is not None:
        return {'key_type': 'special', 'value': key.name}
    elif hasattr(key, 'char') and key.char is not None:
        return {'key_type': 'char', 'value': key.char}
    elif hasattr(key, 'vk') and key.vk is not None:
        return {'key_type': 'vk', 'value': key.vk}
    else:
        return {'key_type': 'unknown', 'value': str(key)}

def deserialize_key(key_dict):
    """Converts a dictionary back to a pynput key event."""
    if not key_dict:
        return None
    key_type = key_dict.get('key_type')
    value = key_dict.get('value')
    
    if key_type == 'special':
        try:
            return getattr(keyboard.Key, value)
        except AttributeError:
            return None
    elif key_type == 'char':
        return keyboard.KeyCode.from_char(value)
    elif key_type == 'vk':
        return keyboard.KeyCode.from_vk(value)
    return None

def serialize_button(button):
    """Converts a pynput mouse button to a string."""
    if button is None:
        return None
    return button.name

def deserialize_button(button_str):
    """Converts a string back to a pynput mouse button."""
    if not button_str:
        return None
    try:
        return getattr(mouse.Button, button_str)
    except AttributeError:
        return None

def serialize_event(event_type, timestamp, **kwargs):
    """Creates a standardized dict structure for recorded events."""
    event = {
        'type': event_type,
        'time': timestamp
    }
    for k, v in kwargs.items():
        if k == 'key':
            event[k] = serialize_key(v)
        elif k == 'button':
            event[k] = serialize_button(v)
        else:
            event[k] = v
    return event

def save_recording(filepath, events):
    """Saves event list to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=4)

def load_recording(filepath):
    """Loads event list from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
