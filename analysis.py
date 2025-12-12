import pandas as pd
import time
import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs

# Load environment variables
load_dotenv()

# === 1. Configuration ===
API_KEY = os.getenv("API_KEY")
INDEX_ID = os.getenv("INDEX_ID")
VIDEO_ID = os.getenv("VIDEO_ID")

if not API_KEY or not INDEX_ID or not VIDEO_ID:
    print("Error: API_KEY, INDEX_ID, or VIDEO_ID not found in environment variables.")
    print("Please create a .env file based on .env.example")
    exit(1)

# Initialize Twelve Labs Client
client = TwelveLabs(api_key=API_KEY)

# === 2. Chapters-based Analysis ===
def analyze_with_chapters():
    """
    Chapters 기능을 사용하여 비디오를 의미있는 챕터로 자동 분할
    - 한 번의 API 호출로 전체 비디오 분석
    - 간결하고 활동 중심의 설명 생성
    - 불필요한 배경 묘사 제거
    """
    print(f"--- Analyzing Video with Chapters: {VIDEO_ID} ---\n")
    
    try:
        print("1. Generating chapters for the entire video...")
        print("   (This may take a moment...)\n")
        
        # Chapters API call
        result = client.summarize(
            video_id=VIDEO_ID,
            type="chapter",  # Key: use "chapter" type
            prompt="""
Generate chapters focused on daily life activities.

Chapter description rules:
- Limit to one or two sentences
- Include only people's main actions (e.g., "using laptop", "watching TV", "cooking", "talking")
- Absolutely exclude background, environment, or object location descriptions
- Include time of day when possible (morning/afternoon/evening)

Good examples:
- "Morning - Husband using laptop and phone at dining table, sharing screen with wife"
- "Afternoon - Couple watching documentary on TV from sofa while talking"
- "Evening - Wife alone on sofa working on laptop while watching TV, with cat"

Bad examples (absolutely forbidden):
- "The video captures a detailed scene..." 
- "The environment is meticulously presented..."
- "The camera is positioned at a high angle..."
- Any descriptions of hallways, boxes, doors, or room layouts

Describe only people's actions and activities concisely.
            """,
            temperature=0.2  # Low value for consistent and concise output
        )
        
        print(f"2. Successfully generated {len(result.chapters)} chapters!\n")
        
        # === 3. 결과 처리 및 저장 ===
        chapters_data = []
        
        print("=" * 80)
        print("CHAPTERS SUMMARY")
        print("=" * 80)
        
        for i, chapter in enumerate(result.chapters, 1):
            # 시간 포맷팅 (초 → 분:초)
            start_min = int(chapter.start // 60)
            start_sec = int(chapter.start % 60)
            end_min = int(chapter.end // 60)
            end_sec = int(chapter.end % 60)
            
            time_range = f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}"
            
            print(f"\n챕터 {i}: {time_range}")
            print(f"  제목: {chapter.chapter_title}")
            if hasattr(chapter, 'chapter_summary') and chapter.chapter_summary:
                print(f"  설명: {chapter.chapter_summary}")
            print("-" * 80)
            
            # 데이터 저장
            chapters_data.append({
                "video_id": VIDEO_ID,
                "chapter_number": i,
                "start_time": chapter.start,
                "end_time": chapter.end,
                "duration_seconds": chapter.end - chapter.start,
                "time_range": time_range,
                "chapter_title": chapter.chapter_title,
                "chapter_summary": getattr(chapter, 'chapter_summary', ''),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # === 4. CSV 저장 ===
        if chapters_data:
            df = pd.DataFrame(chapters_data)
            output_file = "chapters_result.csv"
            df.to_csv(output_file, index=False)
            
            print("\n" + "=" * 80)
            print(f"3. Analysis complete! Results saved to '{output_file}'")
            print("=" * 80)
            print("\n📊 Preview of results:")
            print(df[['chapter_number', 'time_range', 'chapter_title']].to_string(index=False))
            print(f"\n✅ Total chapters: {len(chapters_data)}")
            print(f"✅ Total video duration: ~{int(chapters_data[-1]['end_time'] / 60)} minutes")
            
            return chapters_data
        else:
            print("⚠️  No chapters were generated.")
            return []
            
    except Exception as e:
        print(f"❌ Error during chapter generation: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return []


# === 5. 레거시 함수들 (백업용, 사용 안 함) ===
def search_marengo(query):
    """
    [DEPRECATED] 이전 방식: Search API 사용
    Chapters 방식에서는 사용하지 않음
    """
    try:
        task = client.search.query(
            index_id=INDEX_ID,
            query_text=query,
            search_options=["visual"]
        )
        
        results = []
        for item in task:
            if item.video_id == VIDEO_ID:
                results.append({
                    'start': item.start if item.start is not None else 0.0,
                    'end': item.end if item.end is not None else 0.0,
                    'score': item.score if item.score is not None else 0.0
                })
        return results
    except Exception as e:
        print(f"Search Error: {e}")
        return []


# === 6. Main Entry Point ===
if __name__ == "__main__":
    print("\n" + "🎬" * 40)
    print("  Twelve Labs Video Analysis - Chapters Mode")
    print("🎬" * 40 + "\n")
    
    analyze_with_chapters()
    
    print("\n" + "✨" * 40)
    print("  Analysis Complete!")
    print("✨" * 40 + "\n")
