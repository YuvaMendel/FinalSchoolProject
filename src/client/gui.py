import tkinter as tk
from tkinter import filedialog, messagebox
from client import Client

class ClientGUI:
    def __init__(self, root, client):
        self.root = root
        self.root.title("Client GUI")
        self.root.geometry("400x300")
        self.client = client
        self.create_main_screen()
    
    def create_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Main Menu", font=("Arial", 16)).pack(pady=20)
        
        tk.Button(self.root, text="Upload Image", command=self.open_upload_screen, width=20).pack(pady=5)
        tk.Button(self.root, text="View History", command=self.open_history_screen, width=20).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.root.quit, width=20).pack(pady=5)
    
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
            #self.client.send_file(self.file_path)
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

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root, None)
    root.mainloop()