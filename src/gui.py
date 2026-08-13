import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from pynput import keyboard
import os

from src.recorder import ActionRecorder
from src.player import ActionPlayer
from src.utils import save_recording, load_recording

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def format_event(event):
    """Returns a user-friendly string describing the event."""
    t = f"{event['time']:.2f}s"
    etype = event['type']
    
    if etype == 'mouse_move':
        return f"[{t}] Move to ({event['x']}, {event['y']})"
    elif etype == 'mouse_click':
        action = "Press" if event['pressed'] else "Release"
        return f"[{t}] {action} Mouse {event['button']} at ({event['x']}, {event['y']})"
    elif etype == 'mouse_scroll':
        return f"[{t}] Scroll ({event['dx']}, {event['dy']}) at ({event['x']}, {event['y']})"
    elif etype == 'key_press':
        k_val = event['key']['value']
        return f"[{t}] Press Key: {k_val}"
    elif etype == 'key_release':
        k_val = event['key']['value']
        return f"[{t}] Release Key: {k_val}"
    return f"[{t}] Unknown Event: {etype}"

class AutoClickerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("SunK Macro")
        self.geometry("780x560")
        self.minsize(700, 500)
        
        # State variables
        self.events = []
        self.status = "Idle"
        
        # Initialize modules
        self.recorder = ActionRecorder(
            on_event_callback=self.safe_add_event,
            ignore_keys={keyboard.Key.f8, keyboard.Key.f9}
        )
        self.player = ActionPlayer(
            on_event_played=None,  # Not strictly needed to print during play, but we'll monitor status
            on_status_change=self.safe_status_change
        )
        
        self._build_ui()
        self.update_status_display()

    def _build_ui(self):
        # Configure Grid layout (1 row, 2 columns)
        self.grid_columnconfigure(0, weight=4) # Left controls panel
        self.grid_columnconfigure(1, weight=5) # Right log panel
        self.grid_rowconfigure(0, weight=1)
        
        # ==========================================
        # LEFT PANEL: CONTROLS & SETTINGS
        # ==========================================
        left_panel = ctk.CTkFrame(self, corner_radius=15)
        left_panel.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(3, weight=1) # Push content
        
        # 1. Header Title
        title_lbl = ctk.CTkLabel(
            left_panel, 
            text="SunK Macro", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#10B981"  # Beautiful Emerald / Teal
        )
        title_lbl.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        subtitle_lbl = ctk.CTkLabel(
            left_panel,
            text="Global Hotkeys: F8 = Record | F9 = Playback",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="gray"
        )
        subtitle_lbl.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        
        # 2. Status Indicator Card
        self.status_frame = ctk.CTkFrame(left_panel, corner_radius=8, fg_color="#374151")
        self.status_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_lbl = ctk.CTkLabel(
            self.status_frame, 
            text="STATUS: IDLE", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        self.status_lbl.grid(row=0, column=0, padx=15, pady=12)

        # Container for settings (Recording & Playback)
        settings_container = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        settings_container.grid(row=3, column=0, padx=10, pady=0, sticky="nsew")
        settings_container.grid_columnconfigure(0, weight=1)
        
        # 3. Recording Options Frame
        rec_options_frame = ctk.CTkFrame(settings_container, corner_radius=10)
        rec_options_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        rec_options_frame.grid_columnconfigure(0, weight=1)
        
        rec_header = ctk.CTkLabel(rec_options_frame, text="Recording Options", font=ctk.CTkFont(weight="bold"))
        rec_header.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.check_kb = ctk.CTkCheckBox(rec_options_frame, text="Record Keyboard Keys")
        self.check_kb.select()
        self.check_kb.grid(row=1, column=0, padx=15, pady=5, sticky="w")
        
        self.check_mouse_click = ctk.CTkCheckBox(rec_options_frame, text="Record Mouse Clicks")
        self.check_mouse_click.select()
        self.check_mouse_click.grid(row=2, column=0, padx=15, pady=5, sticky="w")

        self.rec_btn = ctk.CTkButton(
            rec_options_frame, 
            text="Start Recording (F8)", 
            fg_color="#059669", # Green
            hover_color="#047857",
            font=ctk.CTkFont(weight="bold"),
            command=self.toggle_recording
        )
        self.rec_btn.grid(row=3, column=0, padx=15, pady=15, sticky="ew")
        
        # 4. Playback Options Frame
        play_options_frame = ctk.CTkFrame(settings_container, corner_radius=10)
        play_options_frame.grid(row=1, column=0, padx=5, pady=(15, 5), sticky="ew")
        play_options_frame.grid_columnconfigure(0, weight=1)
        play_options_frame.grid_columnconfigure(1, weight=1)
        
        play_header = ctk.CTkLabel(play_options_frame, text="Playback Settings", font=ctk.CTkFont(weight="bold"))
        play_header.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="w")
        
        # Speed multiplier control
        self.speed_lbl = ctk.CTkLabel(play_options_frame, text="Speed Factor: 1.00x")
        self.speed_lbl.grid(row=1, column=0, columnspan=2, padx=15, pady=(5, 0), sticky="w")
        
        self.speed_slider = ctk.CTkSlider(
            play_options_frame, 
            from_=0.25, 
            to=4.0, 
            number_of_steps=15,
            command=self.on_speed_changed
        )
        self.speed_slider.set(1.0)
        self.speed_slider.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")
        
        # Loop delay control
        delay_lbl = ctk.CTkLabel(play_options_frame, text="Loop Delay (sec):")
        delay_lbl.grid(row=3, column=0, padx=15, pady=2, sticky="w")
        self.delay_entry = ctk.CTkEntry(play_options_frame, placeholder_text="0.0", width=80)
        self.delay_entry.insert(0, "0.0")
        self.delay_entry.grid(row=3, column=1, padx=15, pady=2, sticky="e")
        
        # Loop count control
        loop_lbl = ctk.CTkLabel(play_options_frame, text="Loop Repeat Count:")
        loop_lbl.grid(row=4, column=0, padx=15, pady=5, sticky="w")
        self.loop_entry = ctk.CTkEntry(play_options_frame, placeholder_text="1", width=80)
        self.loop_entry.insert(0, "1")
        self.loop_entry.grid(row=4, column=1, padx=15, pady=5, sticky="e")
        
        # Infinite loops checkbox
        self.check_inf = ctk.CTkCheckBox(
            play_options_frame, 
            text="Repeat Infinitely",
            command=self.toggle_infinite_check
        )
        self.check_inf.grid(row=5, column=0, columnspan=2, padx=15, pady=5, sticky="w")
        
        self.play_btn = ctk.CTkButton(
            play_options_frame, 
            text="Play Macro (F9)", 
            fg_color="#2563EB", # Blue
            hover_color="#1D4ED8",
            font=ctk.CTkFont(weight="bold"),
            command=self.toggle_playback
        )
        self.play_btn.grid(row=6, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        
        # ==========================================
        # RIGHT PANEL: EVENT LOGS
        # ==========================================
        right_panel = ctk.CTkFrame(self, corner_radius=15)
        right_panel.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # Log Header
        self.log_header_lbl = ctk.CTkLabel(
            right_panel, 
            text="Action Logs (0 events)", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.log_header_lbl.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # Log Text Box
        self.log_textbox = ctk.CTkTextbox(right_panel, corner_radius=10, state="disabled", wrap="none")
        self.log_textbox.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        
        # File Action Buttons (Save/Load/Clear)
        actions_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        actions_frame.grid(row=2, column=0, padx=15, pady=15, sticky="ew")
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        actions_frame.grid_columnconfigure(2, weight=1)
        
        self.save_btn = ctk.CTkButton(
            actions_frame, 
            text="Save Macro", 
            fg_color="#4B5563", # Grey
            hover_color="#374151",
            command=self.save_macro
        )
        self.save_btn.grid(row=0, column=0, padx=5, pady=0, sticky="ew")
        
        self.load_btn = ctk.CTkButton(
            actions_frame, 
            text="Load Macro", 
            fg_color="#4B5563", 
            hover_color="#374151",
            command=self.load_macro
        )
        self.load_btn.grid(row=0, column=1, padx=5, pady=0, sticky="ew")
        
        self.clear_btn = ctk.CTkButton(
            actions_frame, 
            text="Clear", 
            fg_color="#DC2626", # Red
            hover_color="#B91C1C",
            command=self.clear_events
        )
        self.clear_btn.grid(row=0, column=2, padx=5, pady=0, sticky="ew")

    # ==========================================
    # LOGIC / HANDLERS
    # ==========================================
    
    def on_speed_changed(self, value):
        self.speed_lbl.configure(text=f"Speed Factor: {value:.2f}x")

    def toggle_infinite_check(self):
        if self.check_inf.get() == 1:
            self.loop_entry.configure(state="disabled")
        else:
            self.loop_entry.configure(state="normal")

    def safe_add_event(self, event):
        """Thread-safe event handler called by recorder thread."""
        self.after(0, self.add_event, event)

    def add_event(self, event):
        """Adds event to list and displays in log."""
        self.events.append(event)
        
        # Format and write to text box
        event_str = format_event(event)
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert(tk.END, event_str + "\n")
        self.log_textbox.see(tk.END)
        self.log_textbox.configure(state="disabled")
        
        # Update header
        self.log_header_lbl.configure(text=f"Action Logs ({len(self.events)} events)")

    def safe_status_change(self, status):
        """Thread-safe status handler called by player thread."""
        self.after(0, self.status_change, status)

    def status_change(self, status):
        self.status = status
        self.update_status_display()

    def update_status_display(self):
        if self.status == "Recording":
            self.status_lbl.configure(text="STATUS: RECORDING (Press F8 to stop)")
            self.status_frame.configure(fg_color="#065F46") # Emerald dark
            self.rec_btn.configure(text="Stop Recording (F8)", fg_color="#DC2626", hover_color="#B91C1C")
            self.play_btn.configure(state="disabled")
            self.save_btn.configure(state="disabled")
            self.load_btn.configure(state="disabled")
            self.clear_btn.configure(state="disabled")
        elif self.status == "Playing":
            self.status_lbl.configure(text="STATUS: PLAYING (Press F9 to stop)")
            self.status_frame.configure(fg_color="#1E3A8A") # Blue dark
            self.play_btn.configure(text="Stop Playback (F9)", fg_color="#DC2626", hover_color="#B91C1C")
            self.rec_btn.configure(state="disabled")
            self.save_btn.configure(state="disabled")
            self.load_btn.configure(state="disabled")
            self.clear_btn.configure(state="disabled")
        else:
            self.status_lbl.configure(text="STATUS: IDLE")
            self.status_frame.configure(fg_color="#374151") # Grey dark
            self.rec_btn.configure(text="Start Recording (F8)", fg_color="#059669", hover_color="#047857", state="normal")
            self.play_btn.configure(text="Play Macro (F9)", fg_color="#2563EB", hover_color="#1D4ED8", state="normal")
            self.save_btn.configure(state="normal")
            self.load_btn.configure(state="normal")
            self.clear_btn.configure(state="normal")

    def toggle_recording(self):
        if self.status == "Recording":
            # Stop recording
            recorded = self.recorder.stop()
            self.status = "Idle"
            self.update_status_display()
        elif self.status == "Idle":
            # Clear log before starting a new recording
            self.clear_events()
            
            # Configure filters
            self.recorder.record_keyboard = bool(self.check_kb.get())
            self.recorder.record_mouse_click = bool(self.check_mouse_click.get())
            
            # Start
            self.recorder.start()
            self.status = "Recording"
            self.update_status_display()

    def toggle_playback(self):
        if self.status == "Playing":
            # Stop playback
            self.player.stop()
            self.status = "Idle"
            self.update_status_display()
        elif self.status == "Idle":
            if not self.events:
                messagebox.showwarning("Warning", "There are no events to play. Please record or load a macro first.")
                return
            
            # Parse speed
            self.player.speed_factor = self.speed_slider.get()
            
            # Parse delay between loops
            try:
                self.player.loop_delay = max(0.0, float(self.delay_entry.get()))
            except ValueError:
                self.player.loop_delay = 0.0
                self.delay_entry.delete(0, tk.END)
                self.delay_entry.insert(0, "0.0")
            
            # Parse loops
            if self.check_inf.get() == 1:
                self.player.loop_count = 0  # Infinite
            else:
                try:
                    self.player.loop_count = max(1, int(self.loop_entry.get()))
                except ValueError:
                    self.player.loop_count = 1
                    self.loop_entry.delete(0, tk.END)
                    self.loop_entry.insert(0, "1")
            
            # Start
            self.player.start(self.events)
            self.status = "Playing"
            self.update_status_display()

    def clear_events(self):
        self.events = []
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", tk.END)
        self.log_textbox.configure(state="disabled")
        self.log_header_lbl.configure(text="Action Logs (0 events)")

    def save_macro(self):
        if not self.events:
            messagebox.showwarning("Warning", "Nothing to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Save Macro"
        )
        
        if file_path:
            try:
                save_recording(file_path, self.events)
                messagebox.showinfo("Success", f"Macro successfully saved to:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

    def load_macro(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Load Macro"
        )
        
        if file_path:
            try:
                loaded_events = load_recording(file_path)
                self.clear_events()
                
                # Show loading logs
                self.log_textbox.configure(state="normal")
                for event in loaded_events:
                    self.events.append(event)
                    event_str = format_event(event)
                    self.log_textbox.insert(tk.END, event_str + "\n")
                self.log_textbox.see(tk.END)
                self.log_textbox.configure(state="disabled")
                
                # Update header
                self.log_header_lbl.configure(text=f"Action Logs ({len(self.events)} events)")
                messagebox.showinfo("Success", f"Macro successfully loaded:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {e}")
