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
    def __init__(self, paragraphs, scroll_speed=1.2):
        super().__init__()
        self.title("Teleprompter")
        self.geometry("1000x700")  # increased height for slider
        self.configure(bg="black")

        self.scroll_speed = scroll_speed
        self.scroll_position = 0
        self.is_running = False
        self.start_time = None
        self.last_update_time = None

        # Timer label (top-left)
        self.timer_label = tk.Label(self, text="00:00", fg="white", bg="black", font=("Helvetica", 14))
        self.timer_label.place(x=10, y=10)

        # Canvas for text in center with padding
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.place(x=50, y=50, width=900, height=450)

        self.text_items = []

        y = 50  # Starting y position inside the canvas
        spacing = 20  # Space between paragraphs

        # Create text items, positioning dynamically to avoid overlap
        for paragraph in paragraphs:
            item = self.canvas.create_text(
                450, y,
                text=paragraph,
                font=("Georgia", 24),
                fill="white",
                anchor="n",
                width=800,
                justify="center"
            )
            bbox = self.canvas.bbox(item)
            height = bbox[3] - bbox[1]
            y += height + spacing
            self.text_items.append(item)

        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.max_scroll = max(self.canvas.bbox("all")[3] - self.canvas.winfo_height(), 1)  # prevent div zero

        # Start/Pause button
        self.start_button = tk.Button(self, text="Start / Pause", font=("Helvetica", 16), command=self.toggle_scroll)
        self.start_button.place(relx=0.5, rely=0.9, anchor="center")

        # Scroll position slider (timeline)
        self.slider = tk.Scale(self, from_=0, to=1000, orient='horizontal', length=900,
                               command=self.on_slider_move, showvalue=0, sliderlength=20)
        self.slider.place(x=50, y=530)

        self.user_is_dragging = False
        self.slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)

    def toggle_scroll(self):
        if self.is_running:
            self.is_running = False
        else:
            self.is_running = True
            # Reset start time so timer matches scroll position
            self.start_time = time.time() - (self.scroll_position / self.scroll_speed)
            self.scroll_loop()

    def scroll_loop(self):
        if not self.is_running:
            return

        now = time.time()
        if not self.last_update_time:
            self.last_update_time = now

        elapsed = now - self.start_time

        # Update scroll position based on elapsed time and speed
        self.scroll_position = elapsed * self.scroll_speed
        if self.scroll_position > self.max_scroll:
            self.scroll_position = self.max_scroll
            self.is_running = False  # Stop at bottom

        # Move canvas view
        self.canvas.yview_moveto(self.scroll_position / self.max_scroll)

        # Update timer label
        mins, secs = divmod(int(elapsed), 60)
        self.timer_label.config(text=f"{mins:02}:{secs:02}")

        # Update slider without triggering on_slider_move callback
        self.slider.unbind("<ButtonPress-1>")
        self.slider.unbind("<ButtonRelease-1>")
        self.slider.set(int(self.scroll_position / self.max_scroll * 1000))
        self.slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.slider.bind("<ButtonRelease-1>", self.on_slider_release)

        self.after(40, self.scroll_loop)

    def on_slider_press(self, event):
        self.user_is_dragging = True
        self.is_running = False  # Pause auto scroll while dragging

    def on_slider_release(self, event):
        self.user_is_dragging = False
        # Update scroll position and start_time to sync timer
        pos = self.slider.get() / 1000
        self.scroll_position = pos * self.max_scroll
        self.start_time = time.time() - (self.scroll_position / self.scroll_speed)

    def on_slider_move(self, val):
        if self.user_is_dragging:
            pos = int(val) / 1000
            self.scroll_position = pos * self.max_scroll
            self.canvas.yview_moveto(pos)
            # Update timer label accordingly
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
    app = TeleprompterApp(paragraphs, scroll_speed=12)

    app.mainloop()

if __name__ == "__main__":
    main()
