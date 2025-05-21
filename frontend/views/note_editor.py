"""
Note Editor

This module provides the note editor UI component for the Noterer application.
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import asyncio
from typing import Dict, List, Any, Optional, Callable

from frontend.api_client import APIClient

class NoteEditor(ctk.CTkFrame):
    """Note editor UI component"""
    
    def __init__(self, parent, api_client: APIClient):
        """
        Initialize the note editor
        
        Args:
            parent: Parent widget
            api_client: API client for backend communication
        """
        super().__init__(parent)
        self.api_client = api_client
        self.current_note = None
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI components
        self._create_toolbar()
        self._create_editor()
        self._create_ai_interaction()
        
    def _create_toolbar(self):
        """Create the editor toolbar"""
        self.toolbar = ctk.CTkFrame(self)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Save button
        self.save_btn = ctk.CTkButton(
            self.toolbar,
            text="Save",
            command=self._save_note
        )
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Process with AI button
        self.process_btn = ctk.CTkButton(
            self.toolbar,
            text="Process with AI",
            command=self._process_with_ai
        )
        self.process_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
    def _create_editor(self):
        """Create the text editor"""
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(0, weight=1)
        
        self.text_editor = ctk.CTkTextbox(
            self.editor_frame,
            wrap="word",
            font=("TkDefaultFont", 12)
        )
        self.text_editor.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
    def _create_ai_interaction(self):
        """Create the AI interaction area"""
        self.ai_frame = ctk.CTkFrame(self)
        self.ai_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.ai_frame.grid_columnconfigure(0, weight=1)
        
        # AI query input
        self.ai_entry = ctk.CTkEntry(
            self.ai_frame,
            placeholder_text="Ask AI about this note...",
            height=35
        )
        self.ai_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.ai_btn = ctk.CTkButton(
            self.ai_frame,
            text="Ask AI",
            width=100,
            command=self._query_ai
        )
        self.ai_btn.grid(row=0, column=1, sticky="e", padx=5, pady=5)
        
        # AI response area
        self.ai_response_frame = ctk.CTkFrame(self)
        self.ai_response_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.ai_response_frame.grid_columnconfigure(0, weight=1)
        self.ai_response_frame.grid_rowconfigure(0, weight=1)
        
        self.ai_response = ctk.CTkTextbox(
            self.ai_response_frame,
            wrap="word",
            height=100,
            font=("TkDefaultFont", 12)
        )
        self.ai_response.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.ai_response.configure(state="disabled")
        
    def load_note(self, note: Dict[str, Any]):
        """
        Load a note into the editor
        
        Args:
            note: Note data dictionary
        """
        self.current_note = note
        
        # Clear and update the editor
        self.text_editor.delete("0.0", "end")
        self.text_editor.insert("0.0", note.get("content", ""))
        
        # Clear AI response
        self.ai_response.configure(state="normal")
        self.ai_response.delete("0.0", "end")
        self.ai_response.configure(state="disabled")
        
    def clear(self):
        """Clear the editor for a new note"""
        self.current_note = None
        self.text_editor.delete("0.0", "end")
        
        # Clear AI response
        self.ai_response.configure(state="normal")
        self.ai_response.delete("0.0", "end")
        self.ai_response.configure(state="disabled")
        
    async def _save_note_async(self):
        """Save the current note asynchronously"""
        content = self.text_editor.get("0.0", "end").strip()
        if not content:
            messagebox.showwarning("Warning", "Cannot save empty note")
            return
            
        if self.current_note:
            # Update existing note
            note_id = self.current_note.get("id")
            try:
                updated_note = await self.api_client.update_note(note_id, content)
                self.current_note = updated_note
                messagebox.showinfo("Success", "Note updated successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update note: {str(e)}")
        else:
            # Create new note
            try:
                new_note = await self.api_client.create_note(content)
                self.current_note = new_note
                messagebox.showinfo("Success", "Note created successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create note: {str(e)}")
                
    def _save_note(self):
        """Save the current note (UI callback)"""
        # Use asyncio to run async methods in the main thread
        async def async_save():
            await self._save_note_async()
            
        # Create an event loop that can run in the main thread
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(async_save())
        finally:
            loop.close()
            
    async def _process_with_ai_async(self):
        """Process the current note with AI asynchronously"""
        content = self.text_editor.get("0.0", "end").strip()
        if not content:
            messagebox.showwarning("Warning", "Cannot process empty note")
            return
            
        try:
            result = await self.api_client.process_note(content)
            
            # Display extracted concepts and categories
            self.ai_response.configure(state="normal")
            self.ai_response.delete("0.0", "end")
            
            # Format the response
            response_text = "AI Analysis:\n\n"
            
            if "extracted_concepts" in result:
                response_text += "Concepts: " + ", ".join(result["extracted_concepts"]) + "\n\n"
                
            if "categories" in result:
                response_text += "Categories:\n"
                for cat in result["categories"]:
                    response_text += f"- {cat['name']} ({cat['confidence']:.2f})\n"
                    
            self.ai_response.insert("0.0", response_text)
            self.ai_response.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process note with AI: {str(e)}")
            
    def _process_with_ai(self):
        """Process the current note with AI (UI callback)"""
        # Use asyncio to run async methods in the main thread
        async def async_process():
            await self._process_with_ai_async()
            
        # Create an event loop that can run in the main thread
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(async_process())
        finally:
            loop.close()
            
    async def _query_ai_async(self):
        """Query the AI asynchronously"""
        query = self.ai_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return
            
        content = self.text_editor.get("0.0", "end").strip()
        context_ids = [self.current_note["id"]] if self.current_note else []
        
        try:
            result = await self.api_client.query_ai(query, context_ids)
            
            # Display AI response
            self.ai_response.configure(state="normal")
            self.ai_response.delete("0.0", "end")
            self.ai_response.insert("0.0", result.get("response", "No response from AI"))
            self.ai_response.configure(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to query AI: {str(e)}")
            
    def _query_ai(self):
        """Query the AI (UI callback)"""
        # Use asyncio to run async methods in the main thread
        async def async_query():
            await self._query_ai_async()
            
        # Create an event loop that can run in the main thread
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(async_query())
        finally:
            loop.close()
