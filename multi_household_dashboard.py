import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from deep_translator import GoogleTranslator

# === 1. UI Text Dictionary ===
UI_TEXT = {
    'en': {
        'page_title': 'Multi-Household Video Analysis',
        'main_title': '🏘️ Multi-Household TV Usage Analysis',
        'subtitle': 'Analyzing 6 households × 4 days = 576 hours of video data',
        'overview': '📊 Overview',
        'comparison': '🔄 Household Comparison',
        'timeline': '📈 Timeline Analysis',
        'ai_opportunities': '🤖 AI Opportunities',
        'total_households': 'Total Households',
        'total_days': 'Total Days',
        'total_chapters': 'Total Chapters',
        'total_hours': 'Total Hours Analyzed',
        'select_households': 'Select Households',
        'select_days': 'Select Day Types',
        'all': 'All',
        'weekdays': 'Weekdays',
        'weekends': 'Weekends',
        'language': '🌐 Language',
        'current': 'Current',
        'data_not_found': '⚠️ Multi-household data file not found.',
        'run_batch': 'Please run batch analysis first:\n\n`python batch_analysis.py`',
        'select_all': 'Select All',
        'households_label': 'Households',
        'day_type_label': 'Day Type',
        'household_activity_overview': 'Household Activity Overview',
        'total_activity_by_household': 'Total Activity Time by Household',
        'activity_distribution_time': 'Activity Distribution by Time of Day',
        'activity_count_time': 'Activity Count by Time of Day',
        'activity_pattern_comparison': 'Activity Pattern Comparison',
        'household_comparison_header': 'Household Comparison',
        'select_compare_limit': 'Select households to compare (max 3)',
        'select_compare_min': 'Please select at least 2 households to compare',
        'timeline_analysis_header': 'Timeline Analysis',
        'select_timeline_household': 'Select household for timeline view',
        'activity_timeline_title': '{} - Activity Timeline',
        'chapters_household_header': 'Chapters - Household {}',
        'day_chapters_expander': 'Day {} ({}) - {} chapters',
        'ai_opportunities_header': 'AI Opportunities',
        'ai_coming_soon': '🚧 AI opportunity detection coming soon!',
        'ai_section_desc': 'This section will show:\n- Detected AI opportunities by category\n- Priority scoring\n- Specific use cases with timestamps\n- Implementation recommendations',
    },
    'ko': {
        'page_title': '다중 가구 비디오 분석',
        'main_title': '🏘️ 다중 가구 TV 사용 분석',
        'subtitle': '6가구 × 4일 = 576시간의 비디오 데이터 분석',
        'overview': '📊 개요',
        'comparison': '🔄 가구 비교',
        'timeline': '📈 타임라인 분석',
        'ai_opportunities': '🤖 AI 기회',
        'total_households': '전체 가구',
        'total_days': '전체 일수',
        'total_chapters': '전체 챕터',
        'total_hours': '분석된 총 시간',
        'select_households': '가구 선택',
        'select_days': '요일 유형 선택',
        'all': '전체',
        'weekdays': '평일',
        'weekends': '주말',
        'language': '🌐 언어',
        'current': '현재',
        'data_not_found': '⚠️ 다중 가구 데이터 파일을 찾을 수 없습니다.',
        'run_batch': '먼저 배치 분석을 실행해주세요:\n\n`python batch_analysis.py`',
        'select_all': '전체 선택',
        'households_label': '가구 목록',
        'day_type_label': '요일 유형',
        'household_activity_overview': '가구별 활동 개요',
        'total_activity_by_household': '가구별 총 활동 시간',
        'activity_distribution_time': '시간대별 활동 분포',
        'activity_count_time': '시간대별 활동 빈도',
        'activity_pattern_comparison': '활동 패턴 비교',
        'household_comparison_header': '가구 비교',
        'select_compare_limit': '비교할 가구를 선택하세요 (최대 3개)',
        'select_compare_min': '비교를 위해 최소 2개의 가구를 선택해주세요',
        'timeline_analysis_header': '타임라인 분석',
        'select_timeline_household': '타임라인을 확인할 가구를 선택하세요',
        'activity_timeline_title': '{} - 활동 타임라인',
        'chapters_household_header': '챕터 - 가구 {}',
        'day_chapters_expander': 'Day {} ({}) - 챕터 {}개',
        'ai_opportunities_header': 'AI 기회',
        'ai_coming_soon': '🚧 AI 기회 탐지 기능 준비 중!',
        'ai_section_desc': '이 섹션에서는 다음 내용을 보여줍니다:\n- 카테고리별 탐지된 AI 기회\n- 우선순위 점수\n- 타임스탬프가 포함된 구체적 사례\n- 구현 제안',
    }
}

def t(key):
    """Get translated text"""
    lang = st.session_state.get('language', 'en')
    return UI_TEXT[lang].get(key, key)

# === 2. Page Configuration ===
st.set_page_config(
    page_title=t('page_title'),
    layout="wide",
    page_icon="🏘️"
)

st.title(t('main_title'))
st.markdown(t('subtitle'))

# === 3. Load Data ===
DATA_FILE = "multi_household_analysis.csv"

@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return None
    return pd.read_csv(DATA_FILE)

df = load_data()

if df is None:
    st.warning(t('data_not_found'))
    st.info(t('run_batch'))
    st.stop()

# === 4. Sidebar ===
with st.sidebar:
    st.header("🔧 Controls")
    
    # Language Toggle
    st.write(f"### {t('language')}")
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇺🇸 English", use_container_width=True,
                     type="primary" if st.session_state.language == 'en' else "secondary"):
            st.session_state.language = 'en'
            st.rerun()
    with col2:
        if st.button("🇰🇷 한국어", use_container_width=True,
                     type="primary" if st.session_state.language == 'ko' else "secondary"):
            st.session_state.language = 'ko'
            st.rerun()
    

    
    st.divider()
    
    st.write(f"### {t('select_households')}")
    all_households = sorted(df['household_id'].unique())
    
    # Initialize session state for households if not exists
    if 'selected_households' not in st.session_state:
        st.session_state.selected_households = all_households

    # Select All Button
    if st.button(t('select_all'), key="btn_select_all", use_container_width=True):
        st.session_state.selected_households = all_households
        st.rerun()

    selected_households = st.multiselect(
        t('households_label'),
        all_households,
        default=None,
        key="selected_households",
        label_visibility="collapsed"
    )
    
    # Day Type Filter
    st.write(f"### {t('select_days')}")
    day_filter = st.radio(
        t('day_type_label'),
        [t('all'), t('weekdays'), t('weekends')],
        label_visibility="collapsed"
    )

# Apply Filters
filtered_df = df.copy()

if selected_households:
    filtered_df = filtered_df[filtered_df['household_id'].isin(selected_households)]

if day_filter == t('weekdays'):
    filtered_df = filtered_df[filtered_df['day_type'] == 'weekday']
elif day_filter == t('weekends'):
    filtered_df = filtered_df[filtered_df['day_type'] == 'weekend']

# === 5. Key Metrics ===
st.subheader(t('overview'))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(t('total_households'), len(selected_households))

with col2:
    total_days = filtered_df['day_number'].nunique()
    st.metric(t('total_days'), total_days)

with col3:
    total_chapters = len(filtered_df)
    st.metric(t('total_chapters'), total_chapters)

with col4:
    total_hours = filtered_df['duration_seconds'].sum() / 3600
    st.metric(t('total_hours'), f"{total_hours:.1f}h")

st.divider()

# === 6. Tabs ===
tab1, tab2, tab3, tab4 = st.tabs([
    t('overview'),
    t('comparison'),
    t('timeline'),
    t('ai_opportunities')
])

with tab1:
    st.subheader(t('household_activity_overview'))
    
    # Total chapters by household
    household_summary = filtered_df.groupby('household_id').agg({
        'chapter_number': 'count',
        'duration_seconds': 'sum'
    }).reset_index()
    household_summary['duration_hours'] = household_summary['duration_seconds'] / 3600
    
    fig = px.bar(
        household_summary,
        x='household_id',
        y='duration_hours',
        title=t('total_activity_by_household'),
        labels={'household_id': t('households_label'), 'duration_hours': 'Hours'},
        color='duration_hours',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Time of day distribution
    st.subheader(t('activity_distribution_time'))
    
    time_dist = filtered_df.groupby(['household_id', 'time_of_day']).size().reset_index(name='count')
    
    fig = px.bar(
        time_dist,
        x='household_id',
        y='count',
        color='time_of_day',
        title=t('activity_count_time'),
        labels={'household_id': t('households_label'), 'count': 'Number of Activities'},
        barmode='stack',
        category_orders={'time_of_day': ['morning', 'afternoon', 'evening', 'night']}
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader(t('household_comparison_header'))
    
    # Select households to compare
    compare_households = st.multiselect(
        t('select_compare_limit'),
        selected_households,
        default=selected_households[:min(3, len(selected_households))]
    )
    
    if len(compare_households) >= 2:
        # Radar chart comparison
        metrics = ['morning', 'afternoon', 'evening', 'night']
        
        fig = go.Figure()
        
        for household in compare_households:
            household_data = filtered_df[filtered_df['household_id'] == household]
            values = []
            for metric in metrics:
                count = len(household_data[household_data['time_of_day'] == metric])
                values.append(count)
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metrics,
                fill='toself',
                name=f'Household {household}'
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True,
            title=t('activity_pattern_comparison')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t('select_compare_min'))

with tab3:
    st.subheader(t('timeline_analysis_header'))
    
    # Select a household for timeline
    timeline_household = st.selectbox(
        t('select_timeline_household'),
        selected_households
    )
    
    household_data = filtered_df[filtered_df['household_id'] == timeline_household]
    
    # Create timeline
    fig = px.timeline(
        household_data,
        x_start='start_time',
        x_end='end_time',
        y='day_number',
        color='time_of_day',
        hover_data=['chapter_title'],
        title=t('activity_timeline_title').format(f'Household {timeline_household}'),
        labels={'day_number': 'Day', 'time_of_day': 'Time of Day'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Chapter list
    st.subheader(t('chapters_household_header').format(timeline_household))
    
    for day in sorted(household_data['day_number'].unique()):
        day_data = household_data[household_data['day_number'] == day]
        day_type = day_data['day_type'].iloc[0]
        
        with st.expander(t('day_chapters_expander').format(day, day_type, len(day_data))):
            for _, row in day_data.iterrows():
                st.markdown(f"**{row['time_range']}** - {row['chapter_title']}")
                if row['chapter_summary']:
                    st.caption(row['chapter_summary'])
                st.divider()

with tab4:
    st.subheader(t('ai_opportunities_header'))
    st.info(t('ai_coming_soon'))
    st.markdown(t('ai_section_desc'))

# Footer
st.markdown("---")
st.caption("Powered by Twelve Labs AI • Multi-Household Analysis Dashboard")
