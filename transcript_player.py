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
                    # Normalize whitespace: replace multiple spaces with one
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
        self.geometry("1000x600")
        self.configure(bg="black")

        self.scroll_speed = scroll_speed
        self.scroll_position = 0
        self.is_running = False
        self.start_time = None

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
            bbox = self.canvas.bbox(item)  # Get bounding box of text
            height = bbox[3] - bbox[1]
            y += height + spacing  # Increment y for next paragraph

            self.text_items.append(item)

        # Set scrollable region to fit all text
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Start/Pause button at bottom center
        self.start_button = tk.Button(self, text="Start / Pause", font=("Helvetica", 16), command=self.toggle_scroll)
        self.start_button.place(relx=0.5, rely=0.94, anchor="center")

    def toggle_scroll(self):
        if self.is_running:
            self.is_running = False
        else:
            self.is_running = True
            if not self.start_time:
                self.start_time = time.time()
            self.scroll_loop()

    def scroll_loop(self):
        if not self.is_running:
            return

        # Update timer
        elapsed = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed, 60)
        self.timer_label.config(text=f"{mins:02}:{secs:02}")

        # Scroll
        self.scroll_position += self.scroll_speed
        max_scroll = self.canvas.bbox("all")[3] - self.canvas.winfo_height()
        if self.scroll_position > max_scroll:
            self.scroll_position = max_scroll
            return

        self.canvas.yview_moveto(self.scroll_position / max_scroll)
        self.after(40, self.scroll_loop)

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
