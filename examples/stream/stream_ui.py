import subprocess
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import signal

class StreamUI:
    def __init__(self, master):
        self.master = master
        master.title("Stream Translator")

        # Text area
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(padx=10, pady=10)

        # Frame for controls
        control_frame = tk.Frame(master)
        control_frame.pack(pady=5)

        # Start button
        self.start_button = tk.Button(control_frame, text="Start Translation", command=self.start_translation)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Stop button
        self.stop_button = tk.Button(control_frame, text="Stop Translation", command=self.stop_translation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Font size slider
        self.font_size = tk.IntVar(value=12)
        font_slider = ttk.Scale(control_frame, from_=8, to=24, orient=tk.HORIZONTAL, 
                                variable=self.font_size, command=self.update_font_size)
        font_slider.pack(side=tk.LEFT, padx=5)
        tk.Label(control_frame, text="Font Size").pack(side=tk.LEFT)

        # Set initial font
        self.update_font_size()

        # Translation process
        self.process = None

    def update_font_size(self, *args):
        font_size = self.font_size.get()
        self.text_area.configure(font=("TkDefaultFont", font_size))

    def start_translation(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.text_area.delete('1.0', tk.END)
        threading.Thread(target=self.run_translation, daemon=True).start()

    def stop_translation(self):
        if self.process:
            self.process.terminate()
            self.process = None
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run_translation(self):
        stream_path = "/Users/mike/GitHub/whisper.cpp/stream"
        command = [
            stream_path,
            "-m", "/Users/mike/GitHub/whisper.cpp/models/ggml-small.bin",
            "-t", "8",
            "--step", "0",
            "--length", "30000",
            "-tr",
            "--language", "es",
            "-vth", "0.6"
        ]

        try:
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1, universal_newlines=True)

            for line in self.process.stdout:
                if line.strip() == "[Start speaking]":
                    continue
                
                # Append new text and scroll to the end
                self.text_area.insert(tk.END, line.strip() + "\n")
                self.text_area.see(tk.END)

            # Process has finished
            self.process = None
            self.master.after(0, self.stop_translation)

        except FileNotFoundError:
            self.text_area.insert(tk.END, f"Error: Could not find the stream executable at {stream_path}\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Error: {str(e)}\n")
        finally:
            if self.process:
                self.process.terminate()
                self.process = None
            self.master.after(0, self.stop_translation)

if __name__ == "__main__":
    root = tk.Tk()
    app = StreamUI(root)
    root.mainloop()