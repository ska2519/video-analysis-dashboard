import streamlit as st
import pandas as pd
import os
from deep_translator import GoogleTranslator

# === 1. Page Configuration ===
st.set_page_config(page_title="AI Behavior Analysis Dashboard", layout="wide", page_icon="📺")

st.title("📺 Home Media Usage Analysis Report")
st.markdown("Analysis results using **Twelve Labs Marengo (Visual Search)** & **Pegasus (Generative Video Understanding)**")

# === 2. Translation Setup ===
@st.cache_data
def translate_text(text, target_lang='ko'):
    """
    Translate text to target language using Google Translate
    Cached to avoid repeated API calls for same text
    """
    if not text or text.strip() == "":
        return text
    
    try:
        translator = GoogleTranslator(source='en', target=target_lang)
        # Split long text into chunks (Google Translate has limits)
        if len(text) > 500:
            # Translate in sentences
            sentences = text.split('. ')
            translated = []
            for sentence in sentences:
                if sentence.strip():
                    translated.append(translator.translate(sentence))
            return '. '.join(translated)
        else:
            return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text  # Return original if translation fails

# === 3. Load Data ===
DATA_FILE = "chapters_result.csv"  # Changed to use chapters result

@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return None
    data = pd.read_csv(DATA_FILE)
    return data

df = load_data()

if df is None:
    st.warning("⚠️ Analysis data file (`analysis_result.csv`) not found.")
    st.info("Please run the backend analysis script first:\n\n`python analysis.py`")
    st.stop()

# Helper: Format seconds to MM:SS
def format_time(seconds):
    try:
        m, s = divmod(float(seconds), 60)
        return f"{int(m):02d}:{int(s):02d}"
    except:
        return str(seconds)

df['Start'] = df['start_time'].apply(format_time)
df['End'] = df['end_time'].apply(format_time)
df['Duration'] = df['end_time'] - df['start_time']

# === 3. Key Metrics ===
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Detected Actions", f"{len(df)} counts")

with col2:
    avg_duration = df['Duration'].mean()
    st.metric("Avg. Action Duration", f"{avg_duration:.1f} sec")

with col3:
    video_id_display = df['video_id'].iloc[0] if not df.empty else "-"
    st.metric("Target Video ID", f"{video_id_display[:8]}...") # Show first 8 chars

st.divider()

# === 4. Sidebar Controls & Filtering ===
with st.sidebar:
    st.header("🔧 Analysis Controls")
    
    # Language Toggle (NEW!)
    st.write("### 🌐 Language")
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  # Default to English
    
    col_lang1, col_lang2 = st.columns(2)
    with col_lang1:
        if st.button("🇺🇸 English", use_container_width=True, 
                     type="primary" if st.session_state.language == 'en' else "secondary"):
            st.session_state.language = 'en'
            st.rerun()
    with col_lang2:
        if st.button("🇰🇷 한국어", use_container_width=True,
                     type="primary" if st.session_state.language == 'ko' else "secondary"):
            st.session_state.language = 'ko'
            st.rerun()
    
    st.caption(f"Current: {'English' if st.session_state.language == 'en' else '한국어'}")
    st.divider()
    
    # Toggle: Hide Static Scenes
    st.write("### Filters")
    hide_static = st.toggle("Hide Static/Background Scenes", value=True, help="Filtering out segments described as 'static', 'unchanged', or 'no movement'.")
    
    # Toggle: Person Focus
    show_person_only = st.toggle("Show 'Person' Actions Only", value=False)

    st.divider()

    # Search
    search_term = st.text_input("Search Keywords", placeholder="e.g., phone, bag, walking")
    
    st.info(f"Loaded {len(df)} total segments.")

# Apply Filters
filtered_df = df.copy()

if hide_static:
    # Logic: Only remove if it describes a static scene AND doesn't mention active subjects.
    # 1. Identify "Static" language
    static_keywords = ["static", "unchanged", "no movement", "stillness", "empty hallway"]
    static_pattern = '|'.join(static_keywords)
    is_potentially_static = filtered_df['ai_description'].str.contains(static_pattern, case=False, na=False)
    
    # 2. Identify "Active" language (Safety Valve)
    # If these words exist, it's likely NOT purely static, even if the word 'static' is used in context.
    active_keywords = ["walk", "enter", "leav", "mov", "person", "man", "woman", "carrying", "holding", "interaction"]
    active_pattern = '|'.join(active_keywords)
    has_action = filtered_df['ai_description'].str.contains(active_pattern, case=False, na=False)
    
    # Filter: Keep if (NOT potentially static) OR (Has Action)
    # i.e., Remove only if (Potentially Static AND NO Action)
    mask_to_keep = ~is_potentially_static | has_action
    
    # Debug info logic (optional, but good for trust)
    hidden_count = len(filtered_df) - mask_to_keep.sum()
    if hidden_count > 0:
        st.sidebar.caption(f"ℹ️ Filtered out {hidden_count} static scenes.")
        
    filtered_df = filtered_df[mask_to_keep]

if show_person_only:
    person_keywords = ["person", "man", "woman", "individual", "walking", "holding"]
    pattern = '|'.join(person_keywords)
    filtered_df = filtered_df[filtered_df['ai_description'].str.contains(pattern, case=False, na=False)]

if search_term:
    filtered_df = filtered_df[filtered_df['ai_description'].str.contains(search_term, case=False, na=False)]

# Updated Metrics based on Filter
st.subheader("Key Metrics (Filtered)")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Detected Actions", f"{len(filtered_df)}")
with col2:
    if not filtered_df.empty:
        avg_dur = filtered_df['Duration'].mean()
        st.metric("Avg. Duration", f"{avg_dur:.1f}s")
    else:
        st.metric("Avg. Duration", "0s")
with col3:
    # Calculate 'Active Ratio'
    ratio = (len(filtered_df) / len(df)) * 100
    st.metric("Activity Ratio", f"{ratio:.1f}%")

st.divider()

# === 4. Visualizations (Moved to Top) ===
st.subheader("📊 Visualizations")
tab1, tab2 = st.tabs(["Timeline", "Duration Distribution"])

with tab1:
    st.caption("Distribution of detected actions over video timeline")
    
    # Create 1-minute time bins for heatmap
    if not filtered_df.empty:
        # Convert start_time to minutes (integer)
        filtered_df['Minute'] = (filtered_df['start_time'] // 60).astype(int)
        
        # Count events per minute
        heatmap_data = filtered_df.groupby('Minute').size()
        
        st.bar_chart(heatmap_data, color="#FF4B4B")
        st.caption("X-Axis: Video Time (Minutes) | Y-Axis: Number of Actions")
    else:
        st.write("No data for visualization.")

with tab2:
    st.caption("Histogram of action durations")
    st.bar_chart(filtered_df['Duration'])

st.divider()

# === 5. Activity Feed (Compact Grid) ===
import insights  # Import the new module

# 1. Process Data through Insight Engine
processed_df = insights.deduplicate_events(filtered_df)

st.subheader(f"🎬 Activity Feed ({len(processed_df)} events / {len(filtered_df)} raw)")
st.caption("✨ AI has grouped similar consecutive events to reduce noise.")

if processed_df.empty:
    st.caption("No events match your current filters.")
else:
    # Sophisticated & Minimal CSS (Theme Aware)
    st.markdown("""
    <style>
    .time-label {
        font-size: 0.85em;
        color: gray;
        margin-bottom: 4px;
    }
    .summary-text {
        font-size: 1.05em;
        font-weight: 600;
        color: var(--text-color);
        line-height: 1.4;
    }
    .entity-badge {
        background-color: var(--secondary-background-color);
        color: var(--primary-color);
        font-weight: bold;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8em;
        margin-bottom: 8px;
        display: inline-block;
        border: 1px solid var(--primary-color);
    }
    .tag-span {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid #555;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75em;
        margin-right: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Grid Layout: 2 Columns
    cols = st.columns(2)
    
    for i, (index, row) in enumerate(processed_df.iterrows()):
        # Select column (Alternating)
        current_col = cols[i % 2]
        
        with current_col:
            # Prepare Tags (Multi-label) from the *merged* description
            desc = row['ai_description'].lower()
            tags = []
            
            # Action/Object Tags
            if "phone" in desc or "device" in desc: tags.append("📱 Device")
            if "bag" in desc: tags.append("👜 Bag")
            if "box" in desc or "cardboard" in desc: tags.append("📦 Box")
            if "plate" in desc: tags.append("🍽️ Plate")
            
            # Movement Tags
            if "walking" in desc or "walks" in desc: tags.append("🚶 Walking")
            if "enter" in desc: tags.append("🚪 Enter")
            if "exit" in desc: tags.append("🚪 Exit")
            
            tags_html = "".join([f"<span class='tag-span'>{t}</span>" for t in tags])
            
            # Prepare Text (First sentence of first block)
            # Since merged desc is separated by "|", take the first one for summary
            first_desc = row['ai_description'].split('|')[0]
            summary = first_desc.split('.')[0] + "."
            
            # Render Card container
            with st.container(border=True):
                st.markdown(f"""
                <div class="time-label">⏰ {row['Start']} - {row['End']} ({row['original_count']} events merged)</div>
                <div class="entity-badge">{row['icon']} {row['entity']}</div>
                <div class="summary-text">{summary}</div>
                <div style="margin-top:8px;">{tags_html}</div>
                """, unsafe_allow_html=True)
                
                st.write("") # Spacer
                
                # Native streamline expander for details
                with st.expander("Details", expanded=False):
                    st.caption(row['ai_description'].replace("|", "\n\n--- \n\n"))



# Footer
st.markdown("---")
st.caption("Generated by Twelve Labs Agentic Assistant")
