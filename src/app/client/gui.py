import tkinter as tk
from tkinter import filedialog, messagebox
from client import Client
from PIL import Image, ImageTk
from tkinter import ttk

class ClientGUI:
    
    def __init__(self, client):
        self.root = tk.Tk()
        self.root.title("Client GUI")
        self.root.geometry("400x300")
        self.client = client
        self.load_icons()
        self.connection_label = None  # To store the label
        self.no_internet_img = None  # To store the "No Internet" image
        self.connected_img = None  # To store the "Connected" image
        self.load_images()  # Load the images when initializing
        self.create_main_screen()
        self.file_label = None  # Label to show the selected file path


    def load_icons(self):
        browse_icon = Image.open("static/browse.png")
        browse_icon = browse_icon.resize((20, 20))  # Resize to a good icon size
        self.browse_icon = ImageTk.PhotoImage(browse_icon)  # Store as instance variable to prevent garbage collection
        upload_icon = Image.open("static/upload.png")
        upload_icon = upload_icon.resize((20, 15))  # Resize to a good icon size
        self.upload_icon = ImageTk.PhotoImage(upload_icon)  # Store as instance variable to prevent garbage collection
        exit_icon = Image.open("static/exit.png")
        exit_icon = exit_icon.resize((20, 20))  # Resize to a good icon size
        self.exit_icon = ImageTk.PhotoImage(exit_icon)  # Store as instance variable to prevent garbage collection

    def create_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.update_connection_status()

        tk.Label(self.root, text="Main Menu", font=("Arial", 16)).pack(pady=20)

        ttk.Button(self.root, text="Upload Image", image=self.upload_icon, compound="left",
                   command=self.open_upload_screen, width=20).pack(pady=5)
        ttk.Button(self.root, text="Browse", image=self.browse_icon, compound="left",
                   command=self.open_browse_screen, width=20).pack(pady=5)

        ttk.Button(self.root, text="Exit", image=self.exit_icon, compound="left",
                   command=self.exit_gui, width=20).pack(pady=5)

    def load_images(self):
        # Load images for "No Internet" and "Connected"
        self.no_internet_img = Image.open("static/no_connection.png")  # Replace with your image path
        self.connected_img = Image.open("static/connected.png")  # Replace with your image path
        
        # Resize images if necessary (optional)
        self.no_internet_img.thumbnail((30, 30))
        self.connected_img.thumbnail((30, 30))
        
        # Convert the images to Tkinter-compatible format
        self.no_internet_img = ImageTk.PhotoImage(self.no_internet_img)
        self.connected_img = ImageTk.PhotoImage(self.connected_img)
    def update_connection_status(self):
        if self.connection_label:
            self.connection_label.destroy()
        
        if not self.client.is_connected():
            # Display the "No Internet" image
            self.connection_label = tk.Label(self.root, image=self.no_internet_img)
            self.connection_label.place(x=5, y=5)  # Top-left corner (5 pixels from the top-left)
        else:
            # Display the "Connected" image
            self.connection_label = tk.Label(self.root, image=self.connected_img)
            self.connection_label.place(x=5, y=5)
    def exit_gui(self):
        self.client.close()
        self.root.quit()
    
    
    def open_upload_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Upload Image", font=("Arial", 16)).pack(pady=20)

        self.upload_button = tk.Button(self.root, text="Choose File", command=self.upload_image)
        self.upload_button.pack(pady=10)

        self.file_label = tk.Label(self.root, text="No file selected", wraplength=350)
        self.file_label.pack(pady=5)
        
        self.submit_button = tk.Button(self.root, text="Send", command=self.send_image)
        self.submit_button.pack(pady=10)
        
        tk.Button(self.root, text="Back", command=self.create_main_screen).pack(pady=20)
    
    def upload_image(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if self.file_path:
            self.file_label.config(text=f"Selected: {self.file_path}")

    def start_connection_polling(self, interval_ms=2000):
        self.update_connection_status()
        self.root.after(interval_ms, self.start_connection_polling)

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

        tk.Label(self.root, text="Browse Images", font=("Arial", 16)).pack(pady=10)

        # Filter dropdown menu
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))

        self.filter_var = tk.StringVar(value="All Images")
        options = ["All Images"] + [str(i) for i in range(10)]

        self.filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=options,
                                            state="readonly")
        self.filter_dropdown.pack(side=tk.LEFT)

        # Browse button
        tk.Button(self.root, text="Browse", command=self.browse_images, width=20).pack(pady=10)

        # Back button
        tk.Button(self.root, text="Back", command=self.create_main_screen).pack(pady=10)

    def browse_images(self):
        selected = self.filter_var.get()
        messagebox.showinfo("Filter Selected", f"You selected: {selected}")

    
    def display_result(self, message):
        messagebox.showinfo("Models prediction:", message)

    def activate(self):
        self.start_connection_polling()
        self.root.mainloop()

    def handle_server_response(self, response):
        self.display_result(response)

if __name__ == "__main__":
    app = ClientGUI(None)
    app.activate()