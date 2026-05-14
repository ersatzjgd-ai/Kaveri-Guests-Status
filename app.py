import streamlit as st
from st_supabase_connection import SupabaseConnection
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Guest Status", layout="centered", initial_sidebar_state="collapsed")

# --- CUSTOM CSS ---
# Hides Streamlit chrome, sets up the sticky header, and creates the pulsing animation
custom_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 4rem; /* Room for sticky header */
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

    .stat-pill {
        background: #f0f2f6;
        padding: 4px 12px;
        border-radius: 15px;
        color: #31333F;
    }

    /* Progress Bar Segments */
    .segment {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: bold;
        border-right: 2px solid white;
        transition: all 0.3s ease;
    }
    .segment:last-child {
        border-right: none;
    }

    /* States */
    .state-not-yet { background-color: #E0E0E0; color: #757575; }
    .state-done { background-color: #4CAF50; color: white; }
    .state-done-faded { background-color: #81C784; color: #E8F5E9; } /* Faded green */
    .state-started { 
        background-color: #2196F3; 
        color: white; 
        animation: pulse 1.5s infinite;
        box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7);
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(33, 150, 243, 0); }
        100% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0); }
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

conn = st.connection("supabase", type=SupabaseConnection)

def get_guest_weight(guest):
    """Calculates sorting weight to push active/ready guests to the top."""
    if guest.get('ready_to_meet_gurudev'): return 100
    demo = guest.get('demo_status', 'Not yet')
    lmw = guest.get('lmw_status', 'Not yet')
    
    if demo == 'Started': return 80
    if demo == 'Done': return 70 
    if lmw == 'Started': return 60
    if lmw == 'Done': return 50
    return 0

def get_stage_data(lmw, demo, ready):
    """Determines the CSS class and text for each stage based on progression."""
    # LMW Logic
    if lmw == "Done" and (demo in ["Started", "Done"] or ready):
        c_lmw, t_lmw = "state-done-faded", "LMW Done"
    elif lmw == "Done":
        c_lmw, t_lmw = "state-done", "LMW Done"
    elif lmw == "Started":
        c_lmw, t_lmw = "state-started", "LMW Started"
    else:
        c_lmw, t_lmw = "state-not-yet", "LMW Not yet"

    # Demo Logic
    if demo == "Done" and ready:
        c_demo, t_demo = "state-done-faded", "Demo Done"
    elif demo == "Done":
        c_demo, t_demo = "state-done", "Demo Done"
    elif demo == "Started":
        c_demo, t_demo = "state-started", "Demo Started"
    else:
        c_demo, t_demo = "state-not-yet", "Demo Not yet"

    # Vyas Logic
    if ready:
        c_vyas, t_vyas = "state-done", "Ready for Vyas"
    else:
        c_vyas, t_vyas = "state-not-yet", "Vyas Not yet"

    return (c_lmw, t_lmw), (c_demo, t_demo), (c_vyas, t_vyas)

@st.fragment(run_every="10s")
def display_guest_statuses():
    today_start = f"{datetime.now().strftime('%Y-%m-%d')}T00:00:00"
    
    res = conn.table("guests") \
        .select("guest_name, lmw_status, demo_status, ready_to_meet_gurudev") \
        .eq("is_active", True) \
        .eq("jai_gurudev", False) \
        .gte("created_at", today_start) \
        .execute()
        
    active_guests = res.data

    if not active_guests:
        st.markdown(
            "<div style='text-align: center; color: #757575; margin-top: 50px; font-family: sans-serif;'>"
            "No active guests currently in progress."
            "</div>", 
            unsafe_allow_html=True
        )
        return

    # Calculate Aggregates for Header
    total = len(active_guests)
    lmw_count = sum(1 for g in active_guests if g.get('lmw_status') == 'Started')
    demo_count = sum(1 for g in active_guests if g.get('demo_status') == 'Started')
    ready_count = sum(1 for g in active_guests if g.get('ready_to_meet_gurudev'))

    st.markdown(f"""
        <div class="sticky-header">
            <div class="stat-pill">Total: {total}</div>
            <div class="stat-pill" style="background:#E3F2FD; color:#1976D2;">In LMW: {lmw_count}</div>
            <div class="stat-pill" style="background:#E3F2FD; color:#1976D2;">In Demo: {demo_count}</div>
            <div class="stat-pill" style="background:#E8F5E9; color:#388E3C;">Ready: {ready_count}</div>
        </div>
    """, unsafe_allow_html=True)

    # Sort guests dynamically
    active_guests.sort(key=get_guest_weight, reverse=True)

    # Render Bars
    for guest in active_guests:
        lmw_val = guest.get('lmw_status', 'Not yet')
        demo_val = guest.get('demo_status', 'Not yet')
        ready_val = guest.get('ready_to_meet_gurudev', False)
        
        (c_lmw, t_lmw), (c_demo, t_demo), (c_vyas, t_vyas) = get_stage_data(lmw_val, demo_val, ready_val)
        
        html_bar = f"""
        <div style="margin-bottom: 24px; font-family: sans-serif;">
            <div style="font-size: 20px; font-weight: bold; margin-bottom: 8px; color: #333;">{guest['guest_name']}</div>
            <div style="display: flex; height: 36px; border-radius: 8px; overflow: hidden; background-color: #e0e0e0; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
                <div class="segment {c_lmw}">{t_lmw}</div>
                <div class="segment {c_demo}">{t_demo}</div>
                <div class="segment {c_vyas}">{t_vyas}</div>
            </div>
        </div>
        """
        st.markdown(html_bar, unsafe_allow_html=True)

display_guest_statuses()