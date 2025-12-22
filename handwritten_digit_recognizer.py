import tkinter as tk
from tkinter import colorchooser, messagebox
import PIL
from PIL import Image, ImageDraw, ImageOps
import numpy as np
import os

# ------------------ Model Loading ------------------ #

MODEL_PATH = "mnist_model.h5"
model = None

if not os.path.exists(MODEL_PATH):
    print(f"Error: Model file '{MODEL_PATH}' not found. Please check the path.")
else:
    try:
        from tensorflow.keras.models import load_model
        model = load_model(MODEL_PATH)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None


# ------------------ Main Application ------------------ #

class DigitRecognizerApp(tk.Tk):
    """
    Simple Handwritten Digit Recognizer built with Tkinter + Keras.
    Draw a digit (0–9) on the canvas and click Predict.
    """

    def __init__(self):
        super().__init__()

        # -------- Window config -------- #
        self.title("Handwritten Digit Recognizer")
        self.geometry("500x450")
        self.resizable(False, False)

        # -------- State variables -------- #
        self.brush_size = 12
        self.brush_color = "black"
        self.bg_color = "white"

        # PIL image where drawing is stored
        self.image = PIL.Image.new("L", (280, 280), 255)
        self.draw = ImageDraw.Draw(self.image)

        # -------- UI setup -------- #
        self._build_canvas()
        self._build_controls()
        self._build_statusbar()

        # Bind mouse events
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-1>", self.paint)

        # Keyboard shortcuts
        self.bind("<Control-c>", lambda e: self.clear())
        self.bind("<Return>", lambda e: self.predict())

    # ------------- UI creation methods ------------- #

    def _build_canvas(self):
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(pady=10)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=280,
            height=280,
            bg=self.bg_color,
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.pack()

    def _build_controls(self):
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10)

        # Predict & Clear
        self.predict_btn = tk.Button(control_frame, text="Predict (Enter)", command=self.predict)
        self.predict_btn.grid(row=0, column=0, padx=5)

        self.clear_btn = tk.Button(control_frame, text="Clear (Ctrl+C)", command=self.clear)
        self.clear_btn.grid(row=0, column=1, padx=5)

        # Brush size
        tk.Label(control_frame, text="Brush:").grid(row=0, column=2, padx=(15, 0))
        self.brush_slider = tk.Scale(
            control_frame,
            from_=4,
            to=40,
            orient=tk.HORIZONTAL,
            length=100,
            command=self._update_brush_size
        )
        self.brush_slider.set(self.brush_size)
        self.brush_slider.grid(row=0, column=3, padx=5)

        # Color picker
        self.color_btn = tk.Button(control_frame, text="Color", command=self.choose_color)
        self.color_btn.grid(row=0, column=4, padx=5)

        # Upload image (extra feature)
        self.upload_btn = tk.Button(control_frame, text="Upload 28x28", command=self.upload_image)
        self.upload_btn.grid(row=0, column=5, padx=5)

        # Prediction label
        self.result_label = tk.Label(self, text="Draw a digit and click Predict", font=("Arial", 16))
        self.result_label.pack(pady=10)

    def _build_statusbar(self):
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ------------- Drawing methods ------------- #

    def paint(self, event):
        x, y = event.x, event.y
        r = self.brush_size // 2

        # Draw on Tkinter canvas
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.brush_color, outline=self.brush_color)

        # Draw on PIL image (0 = black, 255 = white)
        color_val = 0 if self.brush_color == "black" else 255
        self.draw.ellipse((x - r, y - r, x + r, y + r), fill=color_val)

    def clear(self):
        self.canvas.delete("all")
        self.image = PIL.Image.new("L", (280, 280), 255)
        self.draw = ImageDraw.Draw(self.image)
        self.result_label.config(text="Canvas cleared. Draw again.")
        self.status_var.set("Canvas cleared")

    def _update_brush_size(self, value):
        self.brush_size = int(value)
        self.status_var.set(f"Brush size: {self.brush_size}")

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose brush color")
        if color[1] is not None:
            self.brush_color = color[1]
            self.status_var.set(f"Brush color: {self.brush_color}")

    # ------------- Prediction methods ------------- #

    def _prepare_image_for_model(self):
        """
        Convert the 280x280 canvas image to a 28x28 normalized array
        suitable for MNIST CNN models.
        """
        img = self.image.resize((28, 28))
        img = ImageOps.invert(img)  # white background -> 0, digit -> 1
        img = np.array(img) / 255.0
        img = img.reshape(1, 28, 28, 1)  # batch, height, width, channels
        return img

    def predict(self):
        if model is None:
            messagebox.showerror("Model Error", "Model not loaded. Check mnist_model.h5 path.")
            self.result_label.config(text="Model not loaded")
            self.status_var.set("Prediction failed: model not loaded")
            return

        try:
            img = self._prepare_image_for_model()
            self.status_var.set("Predicting...")
            prediction = model.predict(img, verbose=0)
            digit = int(np.argmax(prediction))
            confidence = float(np.max(prediction)) * 100.0

            self.result_label.config(
                text=f"Predicted Digit: {digit}  (Confidence: {confidence:.2f}%)"
            )
            self.status_var.set("Prediction complete")
        except Exception as e:
            self.result_label.config(text=f"Error: {str(e)}")
            self.status_var.set("Prediction error")

    # ------------- Extra feature: upload image ------------- #

    def upload_image(self):
        """
        Simple uploader for already preprocessed 28x28 grayscale images.
        Perfect for testing saved MNIST-like images.
        """
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="Select 28x28 grayscale image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )

        if not file_path:
            return

        try:
            img = Image.open(file_path).convert("L").resize((280, 280))
            self.image = img.copy()
            self.draw = ImageDraw.Draw(self.image)

            # Show uploaded image on canvas
            self.canvas.delete("all")
            self.tk_img = PIL.ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)

            self.result_label.config(text="Image loaded. Click Predict.")
            self.status_var.set(f"Loaded image: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image:\n{e}")
            self.status_var.set("Image load error")


# ------------------ Run App ------------------ #

if __name__ == "__main__":
    app = DigitRecognizerApp()
    app.mainloop()
