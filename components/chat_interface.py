"""
Chat interface components for Kiro-style conversational AI
"""
import streamlit as st
from typing import List, Dict, Any
import time

class ChatInterface:
    """Manages the conversational AI interface with Kiro-style interactions"""
    
    def __init__(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "conversation_context" not in st.session_state:
            st.session_state.conversation_context = {}
    
    def display_chat_history(self):
        """Display the chat history with Kiro-style formatting"""
        for message in st.session_state.chat_history:
            self.display_message(
                message["content"], 
                message["role"], 
                message.get("timestamp")
            )
    
    def display_message(self, content: str, role: str, timestamp: str = None):
        """Display a single chat message with proper styling"""
        if role == "user":
            st.markdown(
                f"""
                <div class="chat-message user">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <div style="width: 32px; height: 32px; background: rgba(255,255,255,0.2); 
                                    border-radius: 50%; display: flex; align-items: center; 
                                    justify-content: center; margin-right: 0.75rem;">
                            👤
                        </div>
                        <strong>You</strong>
                        {f'<span style="opacity: 0.7; font-size: 0.85rem; margin-left: auto;">{timestamp}</span>' if timestamp else ''}
                    </div>
                    <div style="margin-left: 2.5rem;">
                        {content}
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="chat-message assistant">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <div style="width: 32px; height: 32px; background: var(--kiro-accent); 
                                    border-radius: 50%; display: flex; align-items: center; 
                                    justify-content: center; margin-right: 0.75rem;">
                            🤖
                        </div>
                        <strong>Kiro</strong>
                        {f'<span style="opacity: 0.7; font-size: 0.85rem; margin-left: auto;">{timestamp}</span>' if timestamp else ''}
                    </div>
                    <div style="margin-left: 2.5rem;">
                        {content}
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    def add_message(self, content: str, role: str):
        """Add a message to the chat history"""
        timestamp = time.strftime("%H:%M")
        st.session_state.chat_history.append({
            "content": content,
            "role": role,
            "timestamp": timestamp
        })
    
    def get_user_input(self, placeholder: str = "Ask Kiro anything...") -> str:
        """Get user input with Kiro-style interface"""
        return st.text_input(
            "Message",
            placeholder=placeholder,
            key="user_input",
            label_visibility="collapsed"
        )
    
    def display_typing_indicator(self):
        """Show typing indicator while AI is processing"""
        with st.empty():
            for i in range(3):
                st.markdown(
                    f"""
                    <div class="chat-message assistant">
                        <div style="display: flex; align-items: center;">
                            <div style="width: 32px; height: 32px; background: var(--kiro-accent); 
                                        border-radius: 50%; display: flex; align-items: center; 
                                        justify-content: center; margin-right: 0.75rem;">
                                🤖
                            </div>
                            <strong>Kiro</strong>
                        </div>
                        <div style="margin-left: 2.5rem; opacity: 0.7;">
                            {'.' * (i + 1)}
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                time.sleep(0.5)
    
    def clear_chat(self):
        """Clear the chat history"""
        st.session_state.chat_history = []
        st.session_state.conversation_context = {}
    
    def export_chat(self) -> str:
        """Export chat history as markdown"""
        markdown_content = "# Kiro Conversation Export\n\n"
        for message in st.session_state.chat_history:
            role_label = "**You:**" if message["role"] == "user" else "**Kiro:**"
            timestamp = message.get("timestamp", "")
            markdown_content += f"{role_label} {timestamp}\n{message['content']}\n\n"
        return markdown_content

class ConversationManager:
    """Manages conversation context and flow"""
    
    def __init__(self):
        self.chat_interface = ChatInterface()
    
    def handle_spec_workflow(self, user_input: str, current_phase: str) -> Dict[str, Any]:
        """Handle spec workflow conversations with proper context"""
        context = {
            "phase": current_phase,
            "user_input": user_input,
            "requires_approval": False,
            "next_action": None
        }
        
        # Determine conversation flow based on current phase
        if current_phase == "requirements":
            context["requires_approval"] = "approve" in user_input.lower() or "looks good" in user_input.lower()
            context["next_action"] = "design" if context["requires_approval"] else "refine_requirements"
        
        elif current_phase == "design":
            context["requires_approval"] = "approve" in user_input.lower() or "looks good" in user_input.lower()
            context["next_action"] = "tasks" if context["requires_approval"] else "refine_design"
        
        elif current_phase == "tasks":
            context["requires_approval"] = "approve" in user_input.lower() or "looks good" in user_input.lower()
            context["next_action"] = "complete" if context["requires_approval"] else "refine_tasks"
        
        return context
    
    def format_kiro_response(self, content: str, response_type: str = "standard") -> str:
        """Format AI responses in Kiro's conversational style"""
        if response_type == "requirements_review":
            return f"I've created the initial requirements document. {content}\n\nTake a look and let me know if you'd like any changes or if we can move forward to the design phase."
        
        elif response_type == "design_review":
            return f"Here's the design document I've put together. {content}\n\nDoes this approach look good to you? If so, we can create the implementation tasks next."
        
        elif response_type == "tasks_review":
            return f"I've broken down the implementation into manageable tasks. {content}\n\nThese should give you a clear roadmap for building the feature. Ready to get started?"
        
        elif response_type == "error":
            return f"Hmm, ran into a small issue there. {content}\n\nLet me try a different approach or feel free to give me more context."
        
        else:
            return content