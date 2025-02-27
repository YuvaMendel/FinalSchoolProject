import tkinter as tk
from tkinter import filedialog, messagebox
from client import Client
from PIL import Image, ImageTk

class ClientGUI:
    
    def __init__(self, client):
        self.root = tk.Tk()
        self.root.title("Client GUI")
        self.root.geometry("400x300")
        self.client = client
        self.connection_label = None  # To store the label
        self.no_internet_img = None  # To store the "No Internet" image
        self.connected_img = None  # To store the "Connected" image
        self.load_images()  # Load the images when initializing
        self.create_main_screen()
    
    def create_main_screen(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Check if the client is connected and display the appropriate label
        self.update_connection_status()
        
        # Create the main menu
        tk.Label(self.root, text="Main Menu", font=("Arial", 16)).pack(pady=20)
        
        tk.Button(self.root, text="Upload Image", command=self.open_upload_screen, width=20).pack(pady=5)
        tk.Button(self.root, text="View History", command=self.open_history_screen, width=20).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.exit_gui, width=20).pack(pady=5)
        
        
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
        
        self.submit_button = tk.Button(self.root, text="Send", command=self.send_image)
        self.submit_button.pack(pady=10)
        
        tk.Button(self.root, text="Back", command=self.create_main_screen).pack(pady=20)
    
    def upload_image(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if self.file_path:
            messagebox.showinfo("File Selected", f"Selected: {self.file_path}")
    
    def send_image(self):
        if hasattr(self, 'file_path') and self.file_path:
            messagebox.showinfo("Success", "Image sent successfully!")
            self.client.send_file(self.file_path)
        else:
            messagebox.showerror("Error", "No file selected!")
    
    def open_history_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="History", font=("Arial", 16)).pack(pady=10)
        
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.history_list = tk.Listbox(frame)
        self.history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_list.yview)
        
        self.load_history()
        
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10, fill=tk.X)
        
        tk.Button(button_frame, text="Back", command=self.create_main_screen, width=20).pack(pady=5)
    
    def load_history(self):
        sample_data = []
        #sample_data = self.client.request_history()
        for item in sample_data:
            self.history_list.insert(tk.END, item)
    
    def display_result(self, message):
        messagebox.showinfo("Server Response", message)
    def activate(self):
        self.root.mainloop()

    def handle_server_response(self, response):
        self.display_result(response)

if __name__ == "__main__":
    app = ClientGUI(None)
    app.activate()