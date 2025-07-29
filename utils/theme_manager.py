import streamlit as st

def get_dark_theme_css():
    """Returns the CSS for dark theme styling"""
    return """
    <style>
        /* Dark theme customizations */
        .stApp {
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            color: #ffffff;
        }
        
        .stSidebar {
            background: linear-gradient(180deg, #2d2d44 0%, #1e1e2e 100%);
            color: #ffffff;
        }
        
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            border-radius: 10px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }
        
        .stSelectbox > div > div > select {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            border-radius: 10px;
        }
        
        .stRadio > div > label {
            color: white;
        }
        
        .stRadio > div > div > div > label {
            color: white;
        }
        
        .stMarkdown {
            color: white;
        }
        
        .stSuccess {
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid rgba(76, 175, 80, 0.5);
            border-radius: 10px;
            padding: 10px;
        }
        
        .stError {
            background: rgba(244, 67, 54, 0.2);
            border: 1px solid rgba(244, 67, 54, 0.5);
            border-radius: 10px;
            padding: 10px;
        }
        
        .stInfo {
            background: rgba(33, 150, 243, 0.2);
            border: 1px solid rgba(33, 150, 243, 0.5);
            border-radius: 10px;
            padding: 10px;
        }
        
        .stWarning {
            background: rgba(255, 152, 0, 0.2);
            border: 1px solid rgba(255, 152, 0, 0.5);
            border-radius: 10px;
            padding: 10px;
        }
        
        /* Chat message styling */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            margin: 10px 0;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Custom title styling */
        .main-title {
            background: linear-gradient(90deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Magic sparkle effect */
        .magic-sparkle {
            position: relative;
        }
        
        .magic-sparkle::before {
            content: "✨";
            position: absolute;
            top: -10px;
            left: -10px;
            animation: sparkle 2s infinite;
        }
        
        @keyframes sparkle {
            0%, 100% { opacity: 0; transform: scale(0.5); }
            50% { opacity: 1; transform: scale(1); }
        }
        
        /* Light theme overrides */
        .light-theme .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333333;
        }
        
        .light-theme .stSidebar {
            background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
            color: #333333;
        }
        
        .light-theme .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .light-theme .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(0, 0, 0, 0.2);
            color: #333333;
        }
        
        .light-theme .stMarkdown {
            color: #333333;
        }
        
        .light-theme .main-title {
            background: linear-gradient(90deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
    </style>
    """

def get_light_theme_css():
    """Returns the CSS for light theme styling"""
    return """
    <style>
        /* Light theme customizations */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333333;
        }
        
        .stSidebar {
            background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
            color: #333333;
        }
        
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(0, 0, 0, 0.2);
            color: #333333;
            border-radius: 10px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }
        
        .stSelectbox > div > div > select {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(0, 0, 0, 0.2);
            color: #333333;
            border-radius: 10px;
        }
        
        .stRadio > div > label {
            color: #333333;
        }
        
        .stRadio > div > div > div > label {
            color: #333333;
        }
        
        .stMarkdown {
            color: #333333;
        }
        
        .stSuccess {
            background: rgba(76, 175, 80, 0.1);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 10px;
            padding: 10px;
        }
        
        .stError {
            background: rgba(244, 67, 54, 0.1);
            border: 1px solid rgba(244, 67, 54, 0.3);
            border-radius: 10px;
            padding: 10px;
        }
        
        .stInfo {
            background: rgba(33, 150, 243, 0.1);
            border: 1px solid rgba(33, 150, 243, 0.3);
            border-radius: 10px;
            padding: 10px;
        }
        
        .stWarning {
            background: rgba(255, 152, 0, 0.1);
            border: 1px solid rgba(255, 152, 0, 0.3);
            border-radius: 10px;
            padding: 10px;
        }
        
        /* Chat message styling */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            margin: 10px 0;
            padding: 15px;
            border: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        /* Custom title styling */
        .main-title {
            background: linear-gradient(90deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Magic sparkle effect */
        .magic-sparkle {
            position: relative;
        }
        
        .magic-sparkle::before {
            content: "✨";
            position: absolute;
            top: -10px;
            left: -10px;
            animation: sparkle 2s infinite;
        }
        
        @keyframes sparkle {
            0%, 100% { opacity: 0; transform: scale(0.5); }
            50% { opacity: 1; transform: scale(1); }
        }
    </style>
    """

def apply_theme(dark_theme=True):
    """Apply the appropriate theme CSS based on the theme setting"""
    if dark_theme:
        st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
    else:
        st.markdown(get_light_theme_css(), unsafe_allow_html=True)

def show_theme_toggle():
    """Display theme toggle in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌙 Theme Settings")
    
    # Initialize theme state if not exists
    if 'dark_theme' not in st.session_state:
        st.session_state.dark_theme = True
    
    dark_theme = st.sidebar.toggle("Dark Theme", value=st.session_state.dark_theme, key="theme_toggle")
    
    if dark_theme != st.session_state.dark_theme:
        st.session_state.dark_theme = dark_theme
        st.rerun()
    
    return dark_theme

def get_title_html():
    """Returns the HTML for the styled title"""
    return '<h1 class="main-title magic-sparkle">🔮 TarotTara – Your Magical Tarot Guide</h1>' 