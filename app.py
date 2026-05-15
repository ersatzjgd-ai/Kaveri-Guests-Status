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
        background-color: rgba(30, 30, 30, 0.95);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        z-index: 1000;
        padding: 12px 0;
        display: flex;
        justify-content: center;
        gap: 15px;
        font-family: sans-serif;
        font-size: 15px;
    }

    /* High-Contrast Stat Pills */
    .stat-pill { 
        padding: 6px 16px; 
        border-radius: 20px; 
        font-weight: 900;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .pill-total { background: #FFFFFF; color: #000000; }
    .pill-ready { background: #00E676; color: #000000; } 
    .pill-progress { background: #FFC107; color: #000000; } 

    /* Section Headers */
    .section-header {
        font-family: sans-serif;
        font-size: 20px;
        font-weight: 900;
        margin-top: 35px;
        margin-bottom: 15px;
        padding-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Custom Header Colors */
    .header-ready { color: #00E676; border-bottom: 2px solid #00E676; text-shadow: 0 0 10px rgba(0, 230, 118, 0.2); }
    .header-progress { color: #FFC107; border-bottom: 2px solid #FFC107; text-shadow: 0 0 10px rgba(255, 193, 7, 0.2); }
    .header-waiting { color: #AAAAAA; border-bottom: 2px solid #444444; }

    /* Guest Card Wrapper */
    .guest-card {
        background-color: #1E1E1E; 
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        font-family: sans-serif;
    }

    /* Guest Name Text (White) */
    .guest-name {
        font-size: 20px; 
        font-weight: bold; 
        margin-bottom: 12px; 
        color: #FFFFFF; 
        letter-spacing: 0.5px;
    }

    /* Progress Bar Segments */
    .segment {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 900; 
        border-right: 2px solid #1E1E1E; 
        transition: all 0.3s ease;
    }
    .segment:last-child { border-right: none; }

    /* STATES */
    .state-not-yet { background-color: #333333; color: #888888; } 
    .state-done { background-color: #00E676; color: #000000; }
    .state-done-faded { background-color: #1B5E20; color: #81C784; } 
    .state-started { 
        background-color: #FFC107; 
        color: #000000; 
        animation: pulse-yellow 1.5s infinite;
        z-index: 10;
    }
    
    /* Special styling for guests who are completely ready */
    .ready-card {
        border-left: 6px solid #00E676;
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.1);
    }

    /* Yellow Pulse Animation */
    @keyframes pulse-yellow {
        0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7); }
        70% { box-shadow: 0 0 0 8px rgba(255, 193, 7, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

conn = st.connection("supabase", type=SupabaseConnection)

def get_guest_weight(guest):
    """Calculates sorting weight to push guests closer to Vyas to the top of their section."""
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

def render_guest_card(guest, is_ready=False):
    """Generates the HTML for a single guest progress bar inside a dark card."""
    lmw_val = guest.get('lmw_status', 'Not yet')
    demo_val = guest.get('demo_status', 'Not yet')
    ready_val = guest.get('ready_to_meet_gurudev', False)
    lounge_val = guest.get('lounge', 'Unknown') 
    
    (c_lmw, t_lmw), (c_demo, t_demo), (c_vyas, t_vyas) = get_stage_data(lmw_val, demo_val, ready_val)
    
    ready_class = "ready-card" if is_ready else ""
    
    html_bar = f"""
    <div class="guest-card {ready_class}">
        <div class="guest-name">👤 {lounge_val} - {guest['guest_name']}</div>
        <div style="display: flex; height: 38px; border-radius: 8px; overflow: hidden; background-color: #222222; box-shadow: inset 0 2px 5px rgba(0,0,0,0.8);">
            <div class="segment {c_lmw}">{t_lmw}</div>
            <div class="segment {c_demo}">{t_demo}</div>
            <div class="segment {c_vyas}">{t_vyas}</div>
        </div>
    </div>
    """
    st.markdown(html_bar, unsafe_allow_html=True)


@st.fragment(run_every="10s")
def display_guest_statuses():
    today_start = f"{datetime.now().strftime('%Y-%m-%d')}T00:00:00"
    
    # ADDED: .eq("met_gurudev", False) so they clear from the board instantly!
    res = conn.table("guests") \
        .select("guest_name, lounge, lmw_status, demo_status, ready_to_meet_gurudev") \
        .eq("is_active", True) \
        .eq("jai_gurudev", False) \
        .eq("met_gurudev", False) \
        .gte("created_at", today_start) \
        .execute()
        
    active_guests = res.data

    if not active_guests:
        st.markdown(
            "<div style='text-align: center; color: #AAAAAA; margin-top: 80px; font-family: sans-serif; font-size: 18px;'>"
            "No active guests currently in progress."
            "</div>", 
            unsafe_allow_html=True
        )
        return

    # Calculate Aggregates
    total = len(active_guests)
    ready_count = sum(1 for g in active_guests if g.get('ready_to_meet_gurudev'))
    in_progress_count = sum(1 for g in active_guests if not g.get('ready_to_meet_gurudev') and (g.get('lmw_status') in ['Started', 'Done'] or g.get('demo_status') in ['Started', 'Done']))
    
    # Render Sticky Top Header
    st.markdown(f"""
        <div class="sticky-header">
            <div class="stat-pill pill-total">TOTAL: {total}</div>
            <div class="stat-pill pill-ready">READY: {ready_count}</div>
            <div class="stat-pill pill-progress">IN PROGRESS: {in_progress_count}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- CATEGORIZE GUESTS ---
    ready_guests = []
    in_progress_guests = []
    waiting_guests = []

    for guest in active_guests:
        if guest.get('ready_to_meet_gurudev'):
            ready_guests.append(guest)
        elif guest.get('lmw_status') in ['Started', 'Done'] or guest.get('demo_status') in ['Started', 'Done']:
            in_progress_guests.append(guest)
        else:
            waiting_guests.append(guest)

    # Sort 'In Progress' queue so those closest to finishing are at the top
    in_progress_guests.sort(key=get_guest_weight, reverse=True)

    # --- RENDER SECTIONS ---
    
    if ready_guests:
        st.markdown('<div class="section-header header-ready">🌟 Ready for Vyas</div>', unsafe_allow_html=True)
        for guest in ready_guests:
            render_guest_card(guest, is_ready=True)
            
    if in_progress_guests:
        st.markdown('<div class="section-header header-progress">🔄 In Progress</div>', unsafe_allow_html=True)
        for guest in in_progress_guests:
            render_guest_card(guest)

    if waiting_guests:
        st.markdown('<div class="section-header header-waiting">⏳ Waiting (Not Started)</div>', unsafe_allow_html=True)
        for guest in waiting_guests:
            render_guest_card(guest)

display_guest_statuses()
