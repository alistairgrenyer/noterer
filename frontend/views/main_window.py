"""
Main Window

This module provides the main window UI for the Noterer application.
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import asyncio
from typing import Dict, Any

from frontend.api_client import APIClient
from frontend.views.note_editor import NoteEditor
from frontend.views.conversation_view import ConversationView
from frontend.services.conversation_service import ConversationService

class MainWindow:
    """Main window UI for the Noterer application"""
    
    def __init__(self, root: ctk.CTk, api_client: APIClient):
        """
        Initialize the main window
        
        Args:
            root: The root CTk window
            api_client: API client for backend communication
        """
        self.root = root
        self.api_client = api_client
        self.notes_data = []  # Store loaded notes data
        
        # Configure root grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=3)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize services
        self.conversation_service = ConversationService(base_url="http://127.0.0.1:8000")
        
        # Create UI components
        self._create_sidebar()
        self._create_content_area()
        
        # Load initial data
        self.root.after(100, self._load_initial_data)
        
    def _create_sidebar(self):
        """Create the sidebar with note list and controls"""
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self.main_frame)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.sidebar)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.new_note_btn = ctk.CTkButton(
            self.header_frame, 
            text="+ New Note", 
            command=self._create_new_note
        )
        self.new_note_btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        # Search frame
        self.search_frame = ctk.CTkFrame(self.sidebar)
        self.search_frame.grid(row=1, column=0, sticky="new", padx=5, pady=5)
        self.search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search notes...")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Notes list
        self.notes_list_frame = ctk.CTkFrame(self.sidebar)
        self.notes_list_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.notes_list_frame.grid_rowconfigure(0, weight=1)
        self.notes_list_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable notes list
        self.notes_list = ctk.CTkScrollableFrame(self.notes_list_frame)
        self.notes_list.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.notes_list.grid_columnconfigure(0, weight=1)
        
    def _create_content_area(self):
        """Create the main content area with tabs"""
        # Content area frame
        self.content_area = ctk.CTkFrame(self.main_frame)
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=0)  # Tab bar
        self.content_area.grid_rowconfigure(1, weight=1)  # Content
        
        # Create tab control
        self.tab_frame = ctk.CTkFrame(self.content_area)
        self.tab_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        self.tab_note = ctk.CTkButton(
            self.tab_frame,
            text="Notes",
            command=self._switch_to_notes_tab,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            corner_radius=0,
            border_spacing=10
        )
        self.tab_note.grid(row=0, column=0, sticky="w", padx=0, pady=0)
        
        self.tab_conversation = ctk.CTkButton(
            self.tab_frame,
            text="Conversation",
            command=self._switch_to_conversation_tab,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            corner_radius=0,
            border_spacing=10
        )
        self.tab_conversation.grid(row=0, column=1, sticky="w", padx=0, pady=0)
        
        # Create content frames for each tab
        # Note editor tab
        self.note_frame = ctk.CTkFrame(self.content_area)
        self.note_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.note_frame.grid_columnconfigure(0, weight=1)
        self.note_frame.grid_rowconfigure(0, weight=1)
        
        self.note_editor = NoteEditor(self.note_frame, self.api_client)
        self.note_editor.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Conversation tab
        self.conversation_frame = ctk.CTkFrame(self.content_area)
        self.conversation_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.conversation_frame.grid_columnconfigure(0, weight=1)
        self.conversation_frame.grid_rowconfigure(0, weight=1)
        
        self.conversation_view = ConversationView(self.conversation_frame, self.conversation_service)
        self.conversation_view.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Start with notes tab active
        self._switch_to_notes_tab()
        
    def _switch_to_notes_tab(self):
        """Switch to the notes tab"""
        self.tab_note.configure(fg_color=("gray75", "gray25"))
        self.tab_conversation.configure(fg_color="transparent")
        self.conversation_frame.grid_remove()
        self.note_frame.grid()
        
    def _switch_to_conversation_tab(self):
        """Switch to the conversation tab"""
        self.tab_conversation.configure(fg_color=("gray75", "gray25"))
        self.tab_note.configure(fg_color="transparent")
        self.note_frame.grid_remove()
        self.conversation_frame.grid()
        
    async def _load_notes(self):
        """Load notes from the backend API"""
        try:
            self.notes_data = await self.api_client.get_notes(limit=20, skip=0)
            self._populate_notes_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {str(e)}")
            
    def _populate_notes_list(self):
        """Populate the notes list with loaded data"""
        # Clear existing items
        for widget in self.notes_list.winfo_children():
            widget.destroy()
            
        # Add notes to the list
        for i, note in enumerate(self.notes_data):
            note_frame = ctk.CTkFrame(self.notes_list)
            note_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            note_frame.grid_columnconfigure(0, weight=1)
            
            # Truncate content for display
            content = note.get("content", "")
            if len(content) > 50:
                content = content[:47] + "..."
                
            note_btn = ctk.CTkButton(
                note_frame,
                text=content,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                anchor="w",
                command=lambda n=note: self._select_note(n)
            )
            note_btn.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
            
    def _select_note(self, note: Dict[str, Any]):
        """Select a note to display in the editor"""
        self.note_editor.load_note(note)
        
    def _create_new_note(self):
        """Create a new empty note"""
        self.note_editor.clear()
        
    def _load_initial_data(self):
        """Load initial data when the application starts"""
        # Use asyncio to run async methods in the main thread
        async def async_load():
            await self._load_notes()
            
        # Create an event loop that can run in the main thread
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(async_load())
        finally:
            loop.close()
            
    def on_closing(self):
        """Handle window closing"""
        # Clean up resources
        self.conversation_view.on_close()
        
        # Exit the application
        self.root.destroy()
