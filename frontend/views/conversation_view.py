"""
Conversation View

This module provides a UI component for conversation-based interactions
with the AI using the confirmation-driven flow.
"""
import customtkinter as ctk
import asyncio
from typing import Optional

from frontend.services.conversation_service import ConversationService

class ConversationView(ctk.CTkFrame):
    """UI component for conversation-based interactions with the AI"""
    
    def __init__(self, parent, conversation_service: Optional[ConversationService] = None):
        """
        Initialize the conversation view
        
        Args:
            parent: Parent widget
            conversation_service: Optional ConversationService instance
        """
        super().__init__(parent)
        
        # Initialize service
        self.conversation_service = conversation_service or ConversationService()
        self.conversation_active = False
        self.awaiting_confirmation = False
        self.proposed_actions = []
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create UI components
        self._create_chat_area()
        self._create_input_area()
        self._create_confirmation_area()
        
        # Initialize conversation
        self.after(100, self._start_conversation)
        
    def _create_chat_area(self):
        """Create the chat history display area"""
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        
        self.chat_display = ctk.CTkTextbox(
            self.chat_frame,
            wrap="word",
            font=("TkDefaultFont", 12)
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.chat_display.configure(state="disabled")
        
        # Welcome message
        self._add_to_chat("System", "Welcome to Noterer! I'm your AI assistant. I'll help you take notes and organize your thoughts.")
        
    def _create_input_area(self):
        """Create the user input area"""
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.user_input = ctk.CTkTextbox(
            self.input_frame,
            height=60,
            wrap="word",
            font=("TkDefaultFont", 12)
        )
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=10)
        
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="Send",
            width=100,
            command=self._send_message
        )
        self.send_btn.grid(row=0, column=1, sticky="e", padx=0, pady=10)
        
    def _create_confirmation_area(self):
        """Create the confirmation area for proposed actions"""
        self.confirmation_frame = ctk.CTkFrame(self)
        self.confirmation_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.confirmation_frame.grid_columnconfigure(0, weight=1)
        
        self.action_display = ctk.CTkTextbox(
            self.confirmation_frame,
            height=100,
            wrap="word",
            font=("TkDefaultFont", 12)
        )
        self.action_display.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(10, 0))
        self.action_display.configure(state="disabled")
        
        self.confirm_btn = ctk.CTkButton(
            self.confirmation_frame,
            text="Confirm",
            fg_color="green",
            width=100,
            command=lambda: self._handle_confirmation(True)
        )
        self.confirm_btn.grid(row=1, column=0, sticky="e", padx=(0, 5), pady=10)
        
        self.reject_btn = ctk.CTkButton(
            self.confirmation_frame,
            text="Reject",
            fg_color="red",
            width=100,
            command=lambda: self._handle_confirmation(False)
        )
        self.reject_btn.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=10)
        
        # Initially hide confirmation area
        self.confirmation_frame.grid_remove()
        
    async def _start_conversation_async(self):
        """Start a new conversation asynchronously"""
        try:
            result = await self.conversation_service.start_conversation()
            self.conversation_active = "conversation_id" in result
            if self.conversation_active:
                self._add_to_chat("System", "Conversation started. How can I help you today?")
            else:
                self._add_to_chat("System", "Failed to start conversation. Please try again.")
        except Exception as e:
            self._add_to_chat("System", f"Error starting conversation: {str(e)}")
    
    def _start_conversation(self):
        """Start a new conversation (UI callback)"""
        asyncio.run(self._start_conversation_async())
        
    def _add_to_chat(self, sender: str, message: str):
        """Add a message to the chat display"""
        self.chat_display.configure(state="normal")
        
        # Format based on sender
        if sender.lower() == "user":
            self.chat_display.insert("end", "You: ", "user_tag")
            self.chat_display.tag_configure("user_tag", foreground="#007bff", font=("TkDefaultFont", 12, "bold"))
        elif sender.lower() == "ai":
            self.chat_display.insert("end", "AI: ", "ai_tag")
            self.chat_display.tag_configure("ai_tag", foreground="#28a745", font=("TkDefaultFont", 12, "bold"))
        else:
            self.chat_display.insert("end", f"{sender}: ", "system_tag")
            self.chat_display.tag_configure("system_tag", foreground="#6c757d", font=("TkDefaultFont", 12, "bold"))
            
        # Add the message and a newline
        self.chat_display.insert("end", f"{message}\n\n")
        
        # Scroll to the bottom
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
        
    def _update_action_display(self, message: str):
        """Update the action display with proposed actions"""
        self.action_display.configure(state="normal")
        self.action_display.delete("1.0", "end")
        self.action_display.insert("end", message)
        self.action_display.configure(state="disabled")
        
    def _clear_user_input(self):
        """Clear the user input field"""
        self.user_input.delete("1.0", "end")
        
    async def _send_message_async(self):
        """Send a message asynchronously"""
        # Get user input
        message = self.user_input.get("1.0", "end").strip()
        if not message:
            return
            
        # Clear input field
        self._clear_user_input()
        
        # Add user message to chat
        self._add_to_chat("User", message)
        
        # Disable input while processing
        self.user_input.configure(state="disabled")
        self.send_btn.configure(state="disabled")
        
        try:
            # Send message to service
            result = await self.conversation_service.send_message(message)
            
            # Add AI response to chat
            if "response" in result:
                self._add_to_chat("AI", result["response"])
                
            # Check if confirmation is required
            if result.get("requires_confirmation", False) and "proposed_actions" in result:
                # Show confirmation area
                self.awaiting_confirmation = True
                self.proposed_actions = result.get("proposed_actions", [])
                
                # Format actions for display
                action_text = "I'd like to make the following changes:\n\n"
                for i, action in enumerate(self.proposed_actions):
                    action_type = action.get("type", "unknown")
                    if action_type == "create_note":
                        action_text += f"{i+1}. Create a new note with content: '{action.get('content', '...')}'\n"
                    elif action_type == "create_concept":
                        action_text += f"{i+1}. Create a new concept: '{action.get('name', '...')}'\n"
                    elif action_type == "create_relationship":
                        action_text += f"{i+1}. Create a relationship between '{action.get('source', '...')}' and '{action.get('target', '...')}'\n"
                    else:
                        action_text += f"{i+1}. {action_type.replace('_', ' ').capitalize()}\n"
                
                action_text += "\nWould you like me to proceed with these changes?"
                self._update_action_display(action_text)
                self.confirmation_frame.grid()
                
                # Keep input disabled until confirmation
                return
                
        except Exception as e:
            self._add_to_chat("System", f"Error: {str(e)}")
            
        finally:
            # Re-enable input if no confirmation required
            if not self.awaiting_confirmation:
                self.user_input.configure(state="normal")
                self.send_btn.configure(state="normal")
    
    def _send_message(self):
        """Send a message (UI callback)"""
        asyncio.run(self._send_message_async())
        
    async def _handle_confirmation_async(self, confirmed: bool):
        """Handle confirmation response asynchronously"""
        try:
            # Process confirmation
            result = await self.conversation_service.confirm_actions(confirmed)
            
            # Add system message to chat
            if confirmed:
                self._add_to_chat("System", "Changes confirmed and applied.")
                
                # Add details about executed actions if available
                if "executed_actions" in result and result["executed_actions"]:
                    executed = result["executed_actions"]
                    success_count = sum(1 for a in executed if a.get("status") == "executed")
                    fail_count = sum(1 for a in executed if a.get("status") == "failed")
                    
                    if fail_count > 0:
                        self._add_to_chat("System", f"Successfully executed {success_count} actions. {fail_count} actions failed.")
                    else:
                        self._add_to_chat("System", f"Successfully executed {success_count} actions.")
            else:
                self._add_to_chat("System", "Changes rejected. How would you like to proceed?")
                
        except Exception as e:
            self._add_to_chat("System", f"Error processing confirmation: {str(e)}")
            
        finally:
            # Reset confirmation state
            self.awaiting_confirmation = False
            self.proposed_actions = []
            
            # Hide confirmation area
            self.confirmation_frame.grid_remove()
            
            # Re-enable input
            self.user_input.configure(state="normal")
            self.send_btn.configure(state="normal")
            
    def _handle_confirmation(self, confirmed: bool):
        """Handle confirmation response (UI callback)"""
        asyncio.run(self._handle_confirmation_async(confirmed))
        
    def on_close(self):
        """Clean up resources when the view is closed"""
        # End the conversation if active
        if self.conversation_active:
            asyncio.run(self.conversation_service.end_conversation())
            
        # Close the session
        asyncio.run(self.conversation_service.close())
