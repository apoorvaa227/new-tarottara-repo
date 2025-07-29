import streamlit as st
import os
import json
import datetime
import re

SESSION_DIR = "sessions"

def load_saved_sessions():
    """Load all saved session files"""
    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)
        return {}
    files = [f for f in os.listdir(SESSION_DIR) if f.endswith(".json")]
    return {f.replace(".json", ""): os.path.join(SESSION_DIR, f) for f in files}

def load_session(filepath):
    """Load a specific session from file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"⚠️ Failed to load session: {e}")
        return {"messages": [], "user_info": {}}

def sanitize_filename(name):
    """Sanitize filename by removing special characters"""
    name = re.sub(r'[^\w\s-]', '', name)
    name = name.strip().replace(' ', '_')
    return name[:40]  # Limit length

def save_session(messages, user_info, session_name=None):
    """Save current session to JSON file"""
    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)
    
    # Generate session name if not provided
    if not session_name:
        if messages and len(messages) > 1:
            # Use the first user question as session name
            for msg in messages:
                if msg.get("role") == "user":
                    question = msg.get("content", "")
                    if question:
                        session_name = sanitize_filename(question)
                        break
        
        if not session_name:
            session_name = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    session_data = {
        "messages": messages,
        "user_info": user_info,
        "created_at": datetime.datetime.now().isoformat(),
        "session_name": session_name
    }
    
    filepath = os.path.join(SESSION_DIR, session_name + ".json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return session_name

def delete_session(session_name):
    """Delete a session file"""
    filepath = os.path.join(SESSION_DIR, session_name + ".json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def show_session_loader():
    """Display session loader interface in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📂 Session Management")
    
    # Toggle session view
    if 'show_sessions' not in st.session_state:
        st.session_state.show_sessions = False
    
    if st.sidebar.button("📂 View Saved Sessions"):
        st.session_state.show_sessions = not st.session_state.show_sessions
    
    if st.session_state.show_sessions:
        st.sidebar.markdown("#### 🧾 Saved Sessions")
        sessions = load_saved_sessions()
        
        if not sessions:
            st.sidebar.info("No saved sessions found.")
            return
        
        for name, path in sessions.items():
            with st.sidebar.expander(f"📄 {name}"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if st.button("🧠 Load", key=f"load_{name}"):
                        session_data = load_session(path)
                        st.session_state.messages = session_data.get("messages", [])
                        st.session_state.user_info = session_data.get("user_info", {})
                        st.success(f"✅ Loaded session: {name}")
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{name}"):
                        if delete_session(name):
                            st.success(f"🗑️ Deleted session: {name}")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to delete session: {name}")

def save_current_session():
    """Save current session with auto-generated name"""
    if st.session_state.messages and len(st.session_state.messages) > 1:
        session_name = save_session(
            st.session_state.messages, 
            st.session_state.user_info
        )
        st.success(f"💾 Session saved as: {session_name}")
        return session_name
    else:
        st.warning("⚠️ No messages to save")
        return None 