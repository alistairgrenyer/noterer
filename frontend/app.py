"""
Noterer Frontend Application

This module provides the main entry point for the Noterer desktop application.
"""
import customtkinter as ctk
import os
import sys
from typing import Optional

from frontend.views.main_window import MainWindow
from frontend.api_client import APIClient

class NotererApp:
    """Main Noterer application class"""
    
    def __init__(self):
        """Initialize the Noterer application"""
        # Set up appearance mode and color theme
        ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"
        
        # Configure backend API client
        self.api_client = APIClient(base_url="http://127.0.0.1:8000")
        
        # Create the main application window
        self.root = ctk.CTk()
        self.root.title("Noterer - AI-Powered Note Taker")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set the icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.root.iconphoto(True, ctk.CTkImage(icon_path))
        
        # Create the main window with all UI components
        self.main_window = MainWindow(self.root, self.api_client)
        
    def run(self):
        """Run the application main loop"""
        self.root.mainloop()
