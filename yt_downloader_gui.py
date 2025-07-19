import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import yt_dlp

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Ranjith's YouTube Downloader 🔥")
        self.root.geometry("550x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#222222")

        self.fg_color = "#f0f0f0"
        self.bg_color = "#222222"
        self.entry_bg = "#333333"
        self.btn_color = "#008fb3"
        self.progress_color = "#00b4d8"

        # URL Input
        ttk.Label(root, text="Enter YouTube URL:", foreground=self.fg_color, background=self.bg_color,
                  font=("Segoe UI", 12, "bold")).pack(pady=(15, 5))
        self.url_entry = tk.Entry(root, width=60, font=("Segoe UI", 10), bg=self.entry_bg, fg=self.fg_color, insertbackground='white')
        self.url_entry.pack()
        self.url_entry.bind("<KeyRelease>", self.on_url_change)

        # Download Type Radio
        frame = tk.Frame(root, bg=self.bg_color)
        frame.pack(pady=10)
        self.dl_type = tk.StringVar(value="video")
        rb_video = ttk.Radiobutton(frame, text="Video + Audio (MP4)", variable=self.dl_type, value="video")
        rb_audio = ttk.Radiobutton(frame, text="Audio Only (MP3)", variable=self.dl_type, value="audio")
        rb_video.grid(row=0, column=0, padx=20)
        rb_audio.grid(row=0, column=1, padx=20)
        self.dl_type.trace_add("write", lambda *args: self.update_quality_options())

        # Quality selection dropdown label
        ttk.Label(root, text="Quality Selection:", foreground=self.fg_color, background=self.bg_color,
                  font=("Segoe UI", 11)).pack()

        self.quality_var = tk.StringVar()
        self.quality_combo = ttk.Combobox(root, textvariable=self.quality_var, state="disabled", width=50,
                                          font=("Segoe UI", 10))
        self.quality_combo.pack(pady=5)
        self.quality_combo.bind("<<ComboboxSelected>>", self.on_quality_selected)

        # Progress bar and status
        self.progress = ttk.Progressbar(root, length=460, mode="determinate")
        self.progress.pack(pady=10)

        self.status_label = tk.Label(root, text="Status: Waiting for URL", fg=self.fg_color, bg=self.bg_color,
                                     font=("Segoe UI", 10, "italic"))
        self.status_label.pack()

        # Download button
        self.download_btn = tk.Button(root, text="Download", bg=self.btn_color, fg="white",
                                      font=("Segoe UI", 12, "bold"), state=tk.DISABLED, command=self.start_download_thread)
        self.download_btn.pack(pady=15)

        # Internal state
        self.download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.format_options = []
        self.format_codes = []

    def on_url_change(self, event=None):
        if hasattr(self, 'fetch_after_id'):
            self.root.after_cancel(self.fetch_after_id)
        url = self.url_entry.get().strip()
        if url.startswith("http"):
            self.status_label.config(text="Status: Valid URL detected, fetching quality options soon...")
            self.quality_combo.set('')
            self.quality_combo['values'] = []
            self.quality_combo.config(state="disabled")
            self.download_btn.config(state=tk.DISABLED)
            self.fetch_after_id = self.root.after(1000, self.update_quality_options)
        else:
            self.status_label.config(text="Status: Waiting for valid URL...")
            self.quality_combo.set('')
            self.quality_combo['values'] = []
            self.quality_combo.config(state="disabled")
            self.download_btn.config(state=tk.DISABLED)

    def update_quality_options(self):
        url = self.url_entry.get().strip()
        if not url.startswith("http"):
            return

        self.status_label.config(text="Status: Fetching quality options...")
        self.quality_combo.set('')
        self.quality_combo['values'] = []
        self.quality_combo.config(state="disabled")
        self.download_btn.config(state=tk.DISABLED)

        def fetch_formats():
            try:
                ydl_opts = {'quiet': True, 'skip_download': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                if self.dl_type.get() == "audio":
                    # Just best audio and some manual choices
                    self.format_options = [
                        "Best audio (automatic)",
                        "128 kbps mp3",
                        "192 kbps mp3",
                        "256 kbps mp3"
                    ]
                    self.format_codes = [
                        "bestaudio/best",
                        "bestaudio[abr<=128]/best",
                        "bestaudio[abr<=192]/best",
                        "bestaudio[abr<=256]/best",
                    ]
                else:
                    # Video + audio combined best or manual
                    self.format_options = [
                        "Best video+audio (automatic)",
                        "720p mp4",
                        "480p mp4",
                        "360p mp4",
                    ]
                    self.format_codes = [
                        "bestvideo+bestaudio/best",
                        "best[height<=720]+bestaudio/best",
                        "best[height<=480]+bestaudio/best",
                        "best[height<=360]+bestaudio/best",
                    ]

                self.quality_combo['values'] = self.format_options
                self.quality_combo.current(0)
                self.quality_combo.config(state="readonly")
                self.status_label.config(text="Status: Quality options loaded! Pick one and download.")
                self.download_btn.config(state=tk.NORMAL)
            except Exception as e:
                self.status_label.config(text="Status: Failed to fetch video info.")
                messagebox.showerror("Error", f"Failed to fetch video info:\n{e}")
                self.download_btn.config(state=tk.DISABLED)
                self.quality_combo.config(state="disabled")

        threading.Thread(target=fetch_formats).start()

    def on_quality_selected(self, event=None):
        if self.quality_combo.current() >= 0:
            self.download_btn.config(state=tk.NORMAL)
        else:
            self.download_btn.config(state=tk.DISABLED)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            try:
                self.progress['value'] = float(percent.strip('%'))
            except:
                pass
            self.status_label.config(text=f"Status: Downloading {percent} at {speed}, ETA: {eta}")
        elif d['status'] == 'finished':
            self.progress['value'] = 100
            self.status_label.config(text="Status: Download complete! Processing...")

    def download(self):
        url = self.url_entry.get().strip()
        if not url or self.quality_combo.current() == -1:
            messagebox.showerror("Error", "Please enter a valid URL and select quality.")
            self.download_btn.config(state=tk.NORMAL)
            return

        format_code = self.format_codes[self.quality_combo.current()]

        ydl_opts = {
            'format': format_code,
            'outtmpl': os.path.join(self.download_folder, '%(title).15s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'noplaylist': True,
        }

        if self.dl_type.get() == "audio":
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.config(text="Status: ✅ Download finished!")
            messagebox.showinfo("Success", "Download completed! Check your Downloads folder.")
        except Exception as e:
            self.status_label.config(text=f"Status: ❌ Error - {e}")
            messagebox.showerror("Download Error", str(e))
        finally:
            self.download_btn.config(state=tk.NORMAL)
            self.progress['value'] = 0

    def start_download_thread(self):
        self.download_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_label.config(text="Status: Starting download...")
        threading.Thread(target=self.download).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)

    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background='#222222', foreground='#f0f0f0', font=('Segoe UI', 10))
    style.configure('TButton', background='#008fb3', foreground='white', font=('Segoe UI', 11, 'bold'))
    style.map('TButton',
              foreground=[('active', 'white')],
              background=[('active', '#00bcd4')])

    root.mainloop()
