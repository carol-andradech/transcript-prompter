import tkinter as tk
from tkinter import filedialog
import time
import re

def clean_text_from_file():
    file_path = filedialog.askopenfilename(
        title="Select your transcript",
        filetypes=[("Text files", "*.txt")]
    )
    if not file_path:
        return []

    paragraphs = []
    timestamp_pattern = re.compile(r'^\((\d{2}:\d{2})\)\s*(.*)')

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            match = timestamp_pattern.match(line)
            if match:
                text = match.group(2)
                if text:
                    text = re.sub(r'\s+', ' ', text)
                    paragraphs.append(text)
            else:
                if paragraphs:
                    line = re.sub(r'\s+', ' ', line)
                    paragraphs[-1] += ' ' + line
                else:
                    line = re.sub(r'\s+', ' ', line)
                    paragraphs.append(line)

    return paragraphs

class TeleprompterApp(tk.Tk):
    def __init__(self, paragraphs, scroll_speed=12):
        super().__init__()

        # Remove window border/title and make always on top
        self.overrideredirect(True)
        self.wm_attributes("-topmost", 1)

        self.configure(bg="black")
        self.geometry("600x600+20+20")  # good size to sit beside YouTube video

        self.scroll_speed = scroll_speed
        self.scroll_position = 0
        self.is_running = False
        self.start_time = None
        self.last_update_time = None

        # Draggable area at the top with close button
        self.drag_area = tk.Frame(self, height=24, bg="black")
        self.drag_area.pack(fill="x")
        self.drag_area.bind("<ButtonPress-1>", self.start_move)
        self.drag_area.bind("<B1-Motion>", self.do_move)

        close_button = tk.Button(self.drag_area, text="✕", font=("Helvetica", 10), fg="white", bg="black",
                                 activebackground="red", activeforeground="white", bd=0,
                                 command=self.destroy)
        close_button.pack(side="right", padx=5)

        # Timer label
        self.timer_label = tk.Label(self, text="00:00", fg="white", bg="black", font=("Helvetica", 12))
        self.timer_label.pack(anchor="w", padx=10)

        # Canvas for text
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0, width=600, height=450)
        self.canvas.pack()

        self.text_items = []

        y = 20
        spacing = 20

        for paragraph in paragraphs:
            item = self.canvas.create_text(
                300, y,
                text=paragraph,
                font=("Georgia", 20),
                fill="white",
                anchor="n",
                width=560,
                justify="center"
            )
            bbox = self.canvas.bbox(item)
            height = bbox[3] - bbox[1]
            y += height + spacing
            self.text_items.append(item)

        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.max_scroll = max(self.canvas.bbox("all")[3] - self.canvas.winfo_height(), 1)

        # Start/Pause button
        self.start_button = tk.Button(self, text="Start / Pause", font=("Helvetica", 12), command=self.toggle_scroll)
        self.start_button.pack(pady=5)

        # Slider for timeline
        self.slider = tk.Scale(self, from_=0, to=1000, orient='horizontal', length=580,
                               command=self.on_slider_move, showvalue=0, sliderlength=15, bg="black", troughcolor="gray")
        self.slider.pack()

        self.user_is_dragging = False
        self.slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.winfo_pointerx() - self._x
        y = self.winfo_pointery() - self._y
        self.geometry(f"+{x}+{y}")

    def toggle_scroll(self):
        if self.is_running:
            self.is_running = False
        else:
            self.is_running = True
            self.start_time = time.time() - (self.scroll_position / self.scroll_speed)
            self.scroll_loop()

    def scroll_loop(self):
        if not self.is_running:
            return

        now = time.time()
        elapsed = now - self.start_time
        self.scroll_position = elapsed * self.scroll_speed

        if self.scroll_position > self.max_scroll:
            self.scroll_position = self.max_scroll
            self.is_running = False

        self.canvas.yview_moveto(self.scroll_position / self.max_scroll)

        mins, secs = divmod(int(elapsed), 60)
        self.timer_label.config(text=f"{mins:02}:{secs:02}")

        self.slider.unbind("<ButtonPress-1>")
        self.slider.unbind("<ButtonRelease-1>")
        self.slider.set(int(self.scroll_position / self.max_scroll * 1000))
        self.slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.after(40, self.scroll_loop)

    def on_slider_press(self, event):
        self.user_is_dragging = True
        self.is_running = False

    def on_slider_release(self, event):
        self.user_is_dragging = False
        pos = self.slider.get() / 1000
        self.scroll_position = pos * self.max_scroll
        self.start_time = time.time() - (self.scroll_position / self.scroll_speed)

    def on_slider_move(self, val):
        if self.user_is_dragging:
            pos = int(val) / 1000
            self.scroll_position = pos * self.max_scroll
            self.canvas.yview_moveto(pos)
            elapsed = self.scroll_position / self.scroll_speed
            mins, secs = divmod(int(elapsed), 60)
            self.timer_label.config(text=f"{mins:02}:{secs:02}")

def main():
    root = tk.Tk()
    root.withdraw()

    paragraphs = clean_text_from_file()
    if not paragraphs:
        print("No usable text found.")
        return

    root.destroy()
    app = TeleprompterApp(paragraphs)
    app.mainloop()

if __name__ == "__main__":
    main()
