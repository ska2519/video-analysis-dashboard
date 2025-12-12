import streamlit as st
import pandas as pd
import os
from deep_translator import GoogleTranslator

# === 1. UI Text Dictionary (Korean/English) ===
UI_TEXT = {
    'en': {
        'page_title': 'Video Analysis Dashboard',
        'main_title': '🎬 Video Chapter Analysis',
        'subtitle': 'Analysis results using **Twelve Labs Chapters** feature',
        'controls': '🔧 Controls',
        'language': '🌐 Language',
        'current': 'Current',
        'total_chapters': 'Total Chapters',
        'video_duration': 'Video Duration',
        'minutes': 'minutes',
        'key_metrics': '📊 Key Metrics',
        'avg_chapter_duration': 'Avg. Chapter Duration',
        'total_video_duration': 'Total Video Duration',
        'sec': 'sec',
        'min': 'min',
        'timeline': '📈 Timeline',
        'timeline_caption': 'Distribution of chapters over video timeline',
        'x_axis': 'X-Axis: Chapter Number',
        'y_axis': 'Y-Axis: Duration (seconds)',
        'chapters': '🎬 Chapters',
        'total': 'total',
        'translating': '🔄 Translating to Korean...',
        'chapter': 'Chapter',
        'details': '📝 Details',
        'raw_data': '📋 Raw Data',
        'view_table': 'View Full Data Table',
        'footer': 'Powered by Twelve Labs AI • Generated with Chapters feature',
        'data_not_found': '⚠️ Chapters data file (`chapters_result.csv`) not found.',
        'run_analysis': 'Please run the analysis script first:\n\n`python analysis.py`',
    },
    'ko': {
        'page_title': '비디오 분석 대시보드',
        'main_title': '🎬 비디오 챕터 분석',
        'subtitle': '**Twelve Labs Chapters** 기능을 사용한 분석 결과',
        'controls': '🔧 컨트롤',
        'language': '🌐 언어',
        'current': '현재',
        'total_chapters': '전체 챕터',
        'video_duration': '비디오 길이',
        'minutes': '분',
        'key_metrics': '📊 주요 지표',
        'avg_chapter_duration': '평균 챕터 길이',
        'total_video_duration': '전체 비디오 길이',
        'sec': '초',
        'min': '분',
        'timeline': '📈 타임라인',
        'timeline_caption': '비디오 타임라인에 따른 챕터 분포',
        'x_axis': 'X축: 챕터 번호',
        'y_axis': 'Y축: 길이 (초)',
        'chapters': '🎬 챕터',
        'total': '개',
        'translating': '🔄 한국어로 번역 중...',
        'chapter': '챕터',
        'details': '📝 상세 내용',
        'raw_data': '📋 원본 데이터',
        'view_table': '전체 데이터 테이블 보기',
        'footer': 'Twelve Labs AI 제공 • Chapters 기능으로 생성',
        'data_not_found': '⚠️ 챕터 데이터 파일 (`chapters_result.csv`)을 찾을 수 없습니다.',
        'run_analysis': '먼저 분석 스크립트를 실행해주세요:\n\n`python analysis.py`',
    }
}

def t(key):
    """Get translated text based on current language"""
    lang = st.session_state.get('language', 'en')
    return UI_TEXT[lang].get(key, key)

# === 2. Page Configuration ===
st.set_page_config(page_title=t('page_title'), layout="wide", page_icon="🎬")

st.title(t('main_title'))
st.markdown(t('subtitle'))

# === 3. Translation Setup (for dynamic content only) ===
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
        st.sidebar.error(f"Translation error: {e}")
        return text  # Return original if translation fails

# === 4. Load Data ===
DATA_FILE = "chapters_result.csv"

@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return None
    data = pd.read_csv(DATA_FILE)
    return data

df = load_data()

if df is None:
    st.warning(t('data_not_found'))
    st.info(t('run_analysis'))
    st.stop()

# === 5. Sidebar Controls ===
with st.sidebar:
    st.header(t('controls'))
    
    # Language Toggle
    st.write(f"### {t('language')}")
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
    

    
    st.divider()
    
    # Info
    st.info(f"""
    **{t('total_chapters')}:** {len(df)}
    
    **{t('video_duration')}:** ~{int(df['end_time'].max() / 60)} {t('minutes')}
    """)

# === 6. Key Metrics ===
st.subheader(t('key_metrics'))
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(t('total_chapters'), f"{len(df)}")

with col2:
    avg_duration = df['duration_seconds'].mean()
    st.metric(t('avg_chapter_duration'), f"{avg_duration:.1f} {t('sec')}")

with col3:
    total_duration = df['end_time'].max()
    st.metric(t('total_video_duration'), f"{int(total_duration / 60)} {t('min')}")

st.divider()

# === 7. Timeline Visualization ===
st.subheader(t('timeline'))
st.caption(t('timeline_caption'))

if not df.empty:
    # Create timeline chart
    timeline_data = df[['chapter_number', 'duration_seconds']].set_index('chapter_number')
    st.bar_chart(timeline_data, color="#FF4B4B")
    st.caption(f"{t('x_axis')} | {t('y_axis')}")

st.divider()

# === 8. Chapters Display ===
st.subheader(f"{t('chapters')} ({len(df)} {t('total')})")

# Apply translation if Korean is selected
display_df = df.copy()

if st.session_state.language == 'ko':
    with st.spinner(t('translating')):
        # Translate chapter titles and summaries
        display_df['chapter_title'] = display_df['chapter_title'].apply(
            lambda x: translate_text(x, 'ko')
        )
        display_df['chapter_summary'] = display_df['chapter_summary'].apply(
            lambda x: translate_text(x, 'ko') if pd.notna(x) and x.strip() != '' else x
        )

# Display chapters in a grid
cols = st.columns(2)

for i, (index, row) in enumerate(display_df.iterrows()):
    current_col = cols[i % 2]
    
    with current_col:
        with st.container(border=True):
            # Chapter header
            st.markdown(f"### 📍 {t('chapter')} {row['chapter_number']}")
            st.caption(f"⏰ {row['time_range']} ({row['duration_seconds']}{t('sec')})")
            
            # Title
            st.markdown(f"**{row['chapter_title']}**")
            
            # Summary (if available)
            if pd.notna(row['chapter_summary']) and row['chapter_summary'].strip() != '':
                with st.expander(t('details'), expanded=False):
                    st.write(row['chapter_summary'])
            
            st.write("")  # Spacer

# === 9. Raw Data Table ===
st.divider()
st.subheader(t('raw_data'))

with st.expander(t('view_table'), expanded=False):
    # Select columns to display
    display_columns = ['chapter_number', 'time_range', 'chapter_title', 'chapter_summary', 'duration_seconds']
    st.dataframe(
        display_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

# Footer
st.markdown("---")
st.caption(t('footer'))
