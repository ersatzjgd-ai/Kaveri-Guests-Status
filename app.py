import streamlit as st
from st_supabase_connection import SupabaseConnection
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Guest Status", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM CSS ---
custom_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 4rem; 
        padding-bottom: 2rem;
    }
    
    /* Sticky Header */
    .sticky-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: rgba(255, 255, 255, 0.95);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        z-index: 1000;
        padding: 10px 0;
        display: flex;
        justify-content: center;
        gap: 20px;
        font-family: sans-serif;
        font-size: 14px;
        font-weight: bold;
    }

    .stat-pill { background: #f0f2f6; padding: 4px 12px; border-radius: 15px; color: #31333F; }

    /* Section Headers */
    .section-header {
        font-family: sans-serif;
        font-size: 18px;
        font-weight: 800;
        color: #555;
        margin-top: 30px;
        margin-bottom: 15px;
        padding-bottom: 5px;
        border-bottom: 2px solid #eee;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Guest Card Wrapper (Dark theme to make white text pop) */
    .guest-card {
        background-color: #1E1E1E; /* Dark background */
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-family: sans-serif;
    }

    /* Guest Name Text (White) */
    .guest-name {
        font-size: 20px; 
        font-weight: bold; 
        margin-bottom: 12px; 
        color: #FFFFFF; /* Changed to White */
        letter-spacing: 0.5px;
    }

    /* Progress Bar Segments */
    .segment {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: bold;
        border-right: 2px solid #1E1E1E; /* Matches card background */
        transition: all 0.3s ease;
    }
    .segment:last-child { border-right: none; }

    /* States */
    .state-not-yet { background-color: #444444; color: #AAAAAA; } /* Darkened for dark card */
    .state-done { background-color: #4CAF50; color: white; }
    .state-done-faded { background-color: #2E7D32; color: #A5D6A7; } 
    
    /* STARTED STATE (Yellow with black text) */
    .state-started { 
        background-color: #FFC107; /* Bright Yellow/Amber */
        color: #000000; /* Black text for high contrast against yellow */
        animation: pulse-yellow 1.5s infinite;
        z-index: 10;
    }
    
    /* Special styling for guests who are completely ready */
    .ready-card {
        border-left: 6px solid #4CAF50;
    }

    /* Yellow Pulse Animation */
    @keyframes pulse-yellow {
        0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7); }
        70% { box-shadow: 0 0 0 8px rgba(255, 193, 7, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
    }
