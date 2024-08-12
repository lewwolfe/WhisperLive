from pathlib import Path
import sys
import threading
import tkinter as tk
from PIL import Image, ImageTk
from whisper_live.client import TranscriptionClient

# Get the current script directory, works in standalone executables and as .py
SCRIPT_DIR = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))


class TranscriptionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Don't Say It...")
        
        self.settings = {
            "username": "Lewwolfe",
            "host": "speech.lewwolfe.net",
            "port": 9090,
            "model": "tiny.en",
            "lang": "en",
            "translate": False,
            "use_vad": True,
            "save_output_recording": False,
            "output_recording_filename": "./output_recording.wav",
            "create_transcript": False
        }

        self.is_muted = False
        self.stop_thread = False
        self.create_widgets()

    def create_client(self):
        self.client = TranscriptionClient(
            self.settings["username"],
            self.settings["host"],
            self.settings["port"],
            lang=self.settings["lang"],
            translate=self.settings["translate"],
            model=self.settings["model"],
            use_vad=self.settings["use_vad"],
            save_output_recording=self.settings["save_output_recording"],
            output_recording_filename=self.settings["output_recording_filename"],
            create_transcript=self.settings["create_transcript"],
            textbox=self.transcript_text
        )

    def create_widgets(self):
        # Settings icon
        settings_img = Image.open(f"{SCRIPT_DIR}/assets/settings_icon.png")
        settings_img = settings_img.resize((25, 25), 0)
        self.settings_icon = ImageTk.PhotoImage(settings_img)
        self.settings_button = tk.Button(self.master, image=self.settings_icon, command=self.open_settings)
        self.settings_button.place(x=380, y=10)

        # Mute/Unmute button
        self.mute_button = tk.Button(self.master, text="Connect", command=self.toggle_mute)
        self.mute_button.place(x=10, y=10)

        # Transcript output area
        self.transcript_text = tk.Text(self.master, wrap=tk.WORD, height=15, width=50)
        self.transcript_text.place(x=10, y=50)

    def connect(self):
        # Start the transcription client
        self.client_thread = threading.Thread(target=self.active_client)
        self.client_thread.daemon = True
        self.client_thread.start()
        self.mute_button.config(text="Mute", bg="green")

    def active_client(self):
        self.create_client()
        self.client()

    def toggle_mute(self):
        if self.mute_button.getvar == "Connect":
            self.connect()
            return

        if self.is_muted:
            self.is_muted = False
            self.mute_button.config(text="Mute", bg="green")
            self.connect()
        else:
            self.is_muted = True
            self.mute_button.config(text="Unmute", bg="red")
            self.client.client.close_websocket()

    def open_settings(self):
        settings_window = tk.Toplevel(self.master)
        settings_window.title("Settings")
        settings_window.geometry("300x300")

        tk.Label(settings_window, text="Username:").grid(row=0, column=0, sticky="e")
        username_entry = tk.Entry(settings_window)
        username_entry.insert(0, self.settings["username"])
        username_entry.grid(row=0, column=1)

        tk.Label(settings_window, text="Host:").grid(row=1, column=0, sticky="e")
        host_entry = tk.Entry(settings_window)
        host_entry.insert(0, self.settings["host"])
        host_entry.grid(row=1, column=1)

        tk.Label(settings_window, text="Port:").grid(row=2, column=0, sticky="e")
        port_entry = tk.Entry(settings_window)
        port_entry.insert(0, self.settings["port"])
        port_entry.grid(row=2, column=1)

        tk.Label(settings_window, text="Model:").grid(row=3, column=0, sticky="e")
        model_entry = tk.Entry(settings_window)
        model_entry.insert(0, self.settings["model"])
        model_entry.grid(row=3, column=1)

        translate_var = tk.BooleanVar(value=self.settings["translate"])
        tk.Label(settings_window, text="Translate:").grid(row=4, column=0, sticky="e")
        translate_checkbox = tk.Checkbutton(settings_window, variable=translate_var)
        translate_checkbox.grid(row=4, column=1)

        tk.Label(settings_window, text="Language:").grid(row=5, column=0, sticky="e")
        lang_entry = tk.Entry(settings_window)
        lang_entry.insert(0, self.settings["lang"])
        lang_entry.grid(row=5, column=1)

        vad_var = tk.BooleanVar(value=self.settings["use_vad"])
        tk.Label(settings_window, text="Voice Auto Detection:").grid(row=6, column=0, sticky="e")
        vad_checkbox = tk.Checkbutton(settings_window, variable=vad_var)
        vad_checkbox.grid(row=6, column=1)

        save_output_recording_var = tk.BooleanVar(value=self.settings["save_output_recording"])
        tk.Label(settings_window, text="Save Output Recording:").grid(row=7, column=0, sticky="e")
        save_output_recording_checkbox = tk.Checkbutton(settings_window, variable=save_output_recording_var)
        save_output_recording_checkbox.grid(row=7, column=1)

        tk.Label(settings_window, text="Output Recording Filename:").grid(row=8, column=0, sticky="e")
        output_recording_filename_entry = tk.Entry(settings_window)
        output_recording_filename_entry.insert(0, self.settings["output_recording_filename"])
        output_recording_filename_entry.grid(row=8, column=1)

        create_transcript_var = tk.BooleanVar(value=self.settings["create_transcript"])
        tk.Label(settings_window, text="Create Transcript:").grid(row=9, column=0, sticky="e")
        create_transcript_checkbox = tk.Checkbutton(settings_window, variable=create_transcript_var)
        create_transcript_checkbox.grid(row=9, column=1)

        def save_settings():
            self.settings["username"] = username_entry.get()
            self.settings["host"] = host_entry.get()
            self.settings["port"] = int(port_entry.get())
            self.settings["model"] = model_entry.get()
            self.settings["translate"] = translate_var.get()
            self.settings["lang"] = lang_entry.get()
            self.settings["use_vad"] = vad_var.get()
            self.settings["save_output_recording"] = save_output_recording_var.get()
            self.settings["output_recording_filename"] = output_recording_filename_entry.get()
            self.settings["create_transcript"] = create_transcript_var.get()
            self.connect()
            settings_window.destroy()

        save_button = tk.Button(settings_window, text="Save", command=save_settings)
        save_button.grid(row=10, column=0, columnspan=2)




if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("425x310")
    app = TranscriptionApp(root)
    root.mainloop()
