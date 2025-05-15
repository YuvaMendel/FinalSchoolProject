import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zipfile, io, csv
from PIL import Image, ImageTk
from client import Client


class ClientGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.exit = False
        self.root.title("DigitNet Client")
        self.root.geometry("400x300")
        self.client = None
        self.logged_in_user = None

        self.load_icons()
        self.no_internet_img = None
        self.connected_img = None
        self.connection_label = None
        self.status_frame = None
        self.login_status_label = None

        self.load_images()
        self.create_main_screen()
        self.file_label = None
        self.root.protocol("WM_DELETE_WINDOW", self.exit_gui)

    def load_icons(self):
        self.browse_icon = ImageTk.PhotoImage(Image.open("static/browse.png").resize((20, 20)))
        self.upload_icon = ImageTk.PhotoImage(Image.open("static/upload.png").resize((20, 15)))
        self.exit_icon = ImageTk.PhotoImage(Image.open("static/exit.png").resize((20, 20)))
        self.login_icon = ImageTk.PhotoImage(Image.open("static/login.png").resize((20, 20)))

    def load_images(self):
        no_net = Image.open("static/no_connection.png")
        connected = Image.open("static/connected.png")
        no_net.thumbnail((30, 30))
        connected.thumbnail((30, 30))
        self.no_internet_img = ImageTk.PhotoImage(no_net)
        self.connected_img = ImageTk.PhotoImage(connected)

    def update_connection_status(self):
        if self.connection_label and self.connection_label.winfo_exists():
            if self.client is None or not self.client.is_connected():
                self.connection_label.config(image=self.no_internet_img)
                self.update_login_status(None)
            else:
                self.connection_label.config(image=self.connected_img)

    def start_connection_polling(self, interval_ms=2000):
        self.update_connection_status()
        self.root.after(interval_ms, self.start_connection_polling)

    def create_status_frame(self):
        if self.status_frame:
            self.status_frame.destroy()

        self.status_frame = tk.Frame(self.root)
        self.status_frame.place(x=5, y=5)

        self.connection_label = tk.Label(self.status_frame)
        self.connection_label.pack(side=tk.LEFT, padx=5)

        self.login_status_label = tk.Label(self.status_frame, text="Not logged in", font=("Arial", 10))
        self.login_status_label.pack(side=tk.LEFT, padx=5)

        self.update_login_status(self.logged_in_user)
        self.update_connection_status()

    def update_login_status(self, username):
        self.logged_in_user = username
        if self.login_status_label and self.login_status_label.winfo_exists():
            if username:
                self.login_status_label.config(text=f"Logged in as: {username}")
            else:
                self.login_status_label.config(text="Not logged in")

    def create_main_screen(self):
        self.file_path = None
        for widget in self.root.winfo_children():
            widget.destroy()

        self.create_status_frame()  # Moved to top

        # Now the title label is pushed below the status bar
        tk.Label(self.root, text="Main Menu", font=("Arial", 16)).pack(pady=(40, 20))

        ttk.Button(self.root, text="Upload Image", image=self.upload_icon, compound="left",
                   command=self.open_upload_screen, width=20).pack(pady=5)
        ttk.Button(self.root, text="Browse", image=self.browse_icon, compound="left",
                   command=self.open_browse_screen, width=20).pack(pady=5)
        ttk.Button(self.root, text="Log in", image=self.login_icon, compound="left",
                   command=self.open_login_screen, width=20).pack(pady=5)
        ttk.Button(self.root, text="Exit", image=self.exit_icon, compound="left",
                   command=self.exit_gui, width=20).pack(pady=5)

        self.create_status_frame()

    def open_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Login / Sign Up", font=("Arial", 16)).pack(pady=(40,20))

        tk.Label(self.root, text="Username:").pack()
        username_entry = tk.Entry(self.root)
        username_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack()
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack(pady=5)

        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            if self.client:
                self.client.request_log_in(username, password)
            else:
                messagebox.showerror("Error", "Client not initialized.")

        def signup():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            if self.client:
                self.client.request_sign_up(username, password)
            else:
                messagebox.showerror("Error", "Client not initialized.")

        tk.Button(self.root, text="Login", command=login).pack(pady=5)
        tk.Button(self.root, text="Sign Up", command=signup).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.create_main_screen).pack(pady=5)

        self.create_status_frame()

    def gui_set_logged_in_user(self, username):
        self.update_login_status(username)

    def exit_gui(self):
        self.exit = True
        if self.client is not None:
            self.client.close()
        self.root.quit()

    def open_upload_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Upload Image", font=("Arial", 16)).pack(pady=(40,20))

        self.upload_button = tk.Button(self.root, text="Choose File", command=self.upload_image)
        self.upload_button.pack(pady=10)

        self.file_label = tk.Label(self.root, text="No file selected", wraplength=350)
        self.file_label.pack(pady=5)

        self.submit_button = tk.Button(self.root, text="Send", command=self.send_image)
        self.submit_button.pack(pady=10)

        tk.Button(self.root, text="Back", command=self.create_main_screen).pack(pady=20)

        self.create_status_frame()

    def upload_image(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if self.file_path:
            self.file_label.config(text=f"Selected: {self.file_path}")

    def send_image(self):
        if hasattr(self, 'file_path') and self.file_path:
            if self.client is not None:
                self.client.send_file(self.file_path)
            else:
                messagebox.showerror("Error", "Client not initialized.")
        else:
            messagebox.showerror("Error", "No file selected!")

    def open_browse_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Browse Images", font=("Arial", 16)).pack(pady=(40,20))

        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))

        self.filter_var = tk.StringVar(value="All Images")
        options = ["All Images"] + [str(i) for i in range(10)]

        self.filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=options,
                                            state="readonly")
        self.filter_dropdown.pack(side=tk.LEFT)

        tk.Button(self.root, text="Browse", command=self.browse_images, width=20).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.create_main_screen).pack(pady=10)

        self.create_status_frame()

    def browse_images(self):
        if self.client is not None:
            digit = self.filter_var.get()
            if digit == "All Images":
                self.client.request_images()
            else:
                self.client.request_images(digit=digit)
        else:
            messagebox.showerror("Error", "Client not initialized.")

    def display_images(self, images):
        self.current_images = images

        for widget in self.root.winfo_children():
            widget.destroy()

        self.image_refs = []

        container = tk.Frame(self.root)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        tk.Label(container, text="Images", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        def update_scrollregion_delayed():
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", lambda e: self.root.after(100, update_scrollregion_delayed))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        max_width, max_height = 100, 100
        min_canvas_width = 100
        columns = 3
        row = 0
        col = 0

        for idx, (img_id, img_pil, digit, confidence) in enumerate(images):
            img_copy = img_pil.copy()
            img_copy.thumbnail((max_width, max_height))
            img_tk = ImageTk.PhotoImage(img_copy)
            self.image_refs.append(img_tk)

            short_id = img_id if len(img_id) <= 5 else img_id[:5] + "..."
            info_text = f"{short_id} | {digit} | {confidence:.2f}"

            frame = tk.Frame(scrollable_frame, padx=5, pady=5)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="n")

            canvas_width = max(min_canvas_width, img_copy.width)

            canvas_img = tk.Canvas(frame, width=canvas_width, height=img_copy.height + 30, highlightthickness=0)
            canvas_img.pack()
            canvas_img.create_image(0, 0, image=img_tk, anchor="nw")
            canvas_img.create_rectangle(0, img_copy.height, canvas_width, img_copy.height + 30, fill="black",
                                        outline="")
            canvas_img.create_text(5, img_copy.height + 15, anchor="w", text=info_text,
                                   fill="white", font=("Arial", 9, "bold"))

            col += 1
            if col >= columns:
                col = 0
                row += 1

        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 60)), "units")
            except Exception:
                pass

        def bind_scroll():
            self.root.bind_all("<MouseWheel>", _on_mousewheel)

        def unbind_scroll():
            self.root.unbind_all("<MouseWheel>")

        bind_scroll()
        self.root.bind("<Destroy>", lambda e: unbind_scroll())

        btn_frame = tk.Frame(self.root)
        btn_frame.grid(row=1, column=0, pady=10)

        tk.Button(btn_frame, text="Back", command=lambda: [unbind_scroll(), self.create_main_screen()]).pack(
            side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Download ZIP", command=self.download_zip).pack(side=tk.RIGHT, padx=10)

        self.create_status_frame()

    def download_zip(self):
        if not hasattr(self, "current_images") or not self.current_images:
            messagebox.showinfo("Info", "No images to export.")
            return

        zip_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")],
            title="Save ZIP Archive"
        )

        if not zip_path:
            return

        try:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                csv_buffer = io.StringIO()
                csv_writer = csv.writer(csv_buffer)
                csv_writer.writerow(["filename", "label", "confidence"])

                for img_id, img_pil, digit, confidence in self.current_images:
                    filename = f"{img_id}.png"
                    img_bytes = io.BytesIO()
                    img_pil.save(img_bytes, format="PNG")
                    img_bytes.seek(0)
                    zipf.writestr(f"images/{filename}", img_bytes.read())
                    csv_writer.writerow([filename, digit, f"{confidence:.4f}"])

                zipf.writestr("labels.csv", csv_buffer.getvalue())

            messagebox.showinfo("Success", f"ZIP file saved to:\n{zip_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save ZIP: {str(e)}")

    def display_result(self, message, message_type="result"):
        if message_type == "result":
            messagebox.showinfo("Result", message)
        elif message_type == "error":
            messagebox.showerror("Error", message)

    def handle_server_response(self, response):
        self.display_result(response)

    def activate(self):
        self.root.after(0, self.start_connection_polling)
        self.root.mainloop()
