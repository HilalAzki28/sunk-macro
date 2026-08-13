import sys
from pynput import keyboard
from tkinter import messagebox
from src.gui import AutoClickerGUI

def main():
    app = AutoClickerGUI()
    
    # Callback for global hotkeys
    def on_press(key):
        if key == keyboard.Key.f8:
            # Safely schedule recording toggle on Tkinter main thread
            app.after(0, app.toggle_recording)
        elif key == keyboard.Key.f9:
            # Safely schedule playback toggle on Tkinter main thread
            app.after(0, app.toggle_playback)

    # Start the global keyboard listener in a background thread
    global_listener = None
    try:
        global_listener = keyboard.Listener(on_press=on_press)
        global_listener.start()
    except Exception as e:
        # Fallback if global hooks cannot be registered
        messagebox.showerror(
            "System Error", 
            f"Failed to register global hotkeys (F8/F9).\n"
            f"Error: {e}\n\n"
            f"The application will run, but you can only control it using the GUI buttons."
        )

    def on_closing():
        """Gracefully shuts down all threads and exits."""
        # Stop global key listener
        if global_listener:
            global_listener.stop()
        
        # Stop recorder background listeners
        try:
            app.recorder.stop()
        except Exception:
            pass
            
        # Stop playback thread
        try:
            app.player.stop()
        except Exception:
            pass
            
        # Destroy window
        app.destroy()
        sys.exit(0)

    # Attach window close handler
    app.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start CustomTkinter GUI main loop
    app.mainloop()

if __name__ == "__main__":
    main()
