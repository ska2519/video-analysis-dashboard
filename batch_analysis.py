"""
Multi-Household Video Analysis - Batch Processing Script

This script processes multiple household videos using Twelve Labs API:
1. Upload videos for each household (A-F) and day (1-4)
2. Generate chapters using Pegasus
3. Detect AI opportunities
4. Save integrated results

Usage:
    python batch_analysis.py --households A B C --days 1 2
"""

import pandas as pd
import time
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from twelvelabs import TwelveLabs
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("API_KEY")
INDEX_ID = os.getenv("INDEX_ID")

if not API_KEY or not INDEX_ID:
    print("Error: API_KEY or INDEX_ID not found in .env file")
    exit(1)

# Initialize client
client = TwelveLabs(api_key=API_KEY)

# Prompts
ACTIVITY_CHAPTER_PROMPT = """
Generate chapters focused on daily life activities.

Chapter description rules:
- Limit to one or two sentences
- Include only people's main actions (e.g., "using laptop", "watching TV", "cooking", "talking")
- Absolutely exclude background, environment, or object location descriptions
- Include time of day when possible (morning/afternoon/evening/night)

Good examples:
- "Morning - Husband using laptop and phone at dining table, sharing screen with wife"
- "Afternoon - Couple watching documentary on TV from sofa while talking"
- "Evening - Wife alone on sofa working on laptop while watching TV, with cat"

Bad examples (absolutely forbidden):
- "The video captures a detailed scene..." 
- "The environment is meticulously presented..."
- Any descriptions of hallways, boxes, doors, or room layouts

Describe only people's actions and activities concisely.
"""


def upload_video(video_path, household_id, day_number):
    """
    Upload a video to Twelve Labs and wait for indexing
    
    Args:
        video_path: Path to video file
        household_id: Household identifier (A-F)
        day_number: Day number (1-4)
    
    Returns:
        video_id: Twelve Labs video ID
    """
    print(f"\n📤 Uploading: Household {household_id}, Day {day_number}")
    print(f"   File: {video_path}")
    
    try:
        task = client.task.create(
            index_id=INDEX_ID,
            file=video_path,
            language="en"
        )
        
        print(f"   Task ID: {task.id}")
        print(f"   Waiting for indexing...", end="", flush=True)
        
        # Wait for indexing to complete
        task.wait_for_done()
        
        print(" ✓ Done")
        print(f"   Video ID: {task.video_id}")
        
        return task.video_id
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        return None


def generate_chapters(video_id, household_id, day_number):
    """
    Generate chapters for a video using Pegasus
    
    Args:
        video_id: Twelve Labs video ID
        household_id: Household identifier
        day_number: Day number
    
    Returns:
        list: Chapter data dictionaries
    """
    print(f"\n🎬 Generating chapters: Household {household_id}, Day {day_number}")
    
    try:
        result = client.summarize(
            video_id=video_id,
            type="chapter",
            prompt=ACTIVITY_CHAPTER_PROMPT,
            temperature=0.2
        )
        
        chapters_data = []
        
        for i, chapter in enumerate(result.chapters, 1):
            # Determine day type
            day_type = "weekday" if day_number in [1, 2] else "weekend"
            
            # Determine time of day
            hour = int(chapter.start // 3600)
            if 6 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 18:
                time_of_day = "afternoon"
            elif 18 <= hour < 24:
                time_of_day = "evening"
            else:
                time_of_day = "night"
            
            # Format time range
            start_min = int(chapter.start // 60)
            start_sec = int(chapter.start % 60)
            end_min = int(chapter.end // 60)
            end_sec = int(chapter.end % 60)
            time_range = f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}"
            
            chapter_data = {
                "household_id": household_id,
                "day_number": day_number,
                "day_type": day_type,
                "video_id": video_id,
                "chapter_number": i,
                "start_time": chapter.start,
                "end_time": chapter.end,
                "duration_seconds": chapter.end - chapter.start,
                "time_of_day": time_of_day,
                "time_range": time_range,
                "chapter_title": chapter.chapter_title,
                "chapter_summary": getattr(chapter, 'chapter_summary', ''),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            chapters_data.append(chapter_data)
        
        print(f"   ✓ Generated {len(chapters_data)} chapters")
        
        return chapters_data
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def process_household(household_id, days, video_dir="videos"):
    """
    Process all videos for a single household
    
    Args:
        household_id: Household identifier (A-F)
        days: List of day numbers to process
        video_dir: Directory containing video files
    
    Returns:
        list: All chapter data for this household
    """
    print(f"\n{'='*60}")
    print(f"Processing Household {household_id}")
    print(f"{'='*60}")
    
    all_chapters = []
    
    for day in days:
        # Check if video file exists
        video_filename = f"household_{household_id}_day{day}.mp4"
        video_path = Path(video_dir) / video_filename
        
        if not video_path.exists():
            print(f"\n⚠️  Video not found: {video_path}")
            print(f"   Skipping Household {household_id}, Day {day}")
            continue
        
        # Upload video
        video_id = upload_video(str(video_path), household_id, day)
        
        if not video_id:
            print(f"   Skipping chapter generation due to upload failure")
            continue
        
        # Generate chapters
        chapters = generate_chapters(video_id, household_id, day)
        all_chapters.extend(chapters)
        
        # Rate limiting
        time.sleep(2)
    
    return all_chapters


def main():
    parser = argparse.ArgumentParser(description="Batch process household videos")
    parser.add_argument(
        "--households",
        nargs="+",
        default=["A", "B", "C", "D", "E", "F"],
        help="Household IDs to process (default: all A-F)"
    )
    parser.add_argument(
        "--days",
        nargs="+",
        type=int,
        default=[1, 2, 3, 4],
        help="Day numbers to process (default: all 1-4)"
    )
    parser.add_argument(
        "--video-dir",
        default="videos",
        help="Directory containing video files (default: videos)"
    )
    parser.add_argument(
        "--output",
        default="multi_household_analysis.csv",
        help="Output CSV file (default: multi_household_analysis.csv)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "🎬" * 30)
    print("Multi-Household Video Analysis - Batch Processing")
    print("🎬" * 30)
    print(f"\nHouseholds: {', '.join(args.households)}")
    print(f"Days: {', '.join(map(str, args.days))}")
    print(f"Video directory: {args.video_dir}")
    print(f"Output file: {args.output}")
    
    # Process all households
    all_data = []
    
    for household_id in args.households:
        chapters = process_household(household_id, args.days, args.video_dir)
        all_data.extend(chapters)
    
    # Save results
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(args.output, index=False)
        
        print(f"\n{'='*60}")
        print(f"✅ Analysis Complete!")
        print(f"{'='*60}")
        print(f"\nTotal chapters: {len(all_data)}")
        print(f"Households processed: {df['household_id'].nunique()}")
        print(f"Days processed: {df['day_number'].nunique()}")
        print(f"\nResults saved to: {args.output}")
        
        # Summary statistics
        print(f"\n📊 Summary by Household:")
        summary = df.groupby('household_id').agg({
            'chapter_number': 'count',
            'duration_seconds': 'sum'
        }).rename(columns={
            'chapter_number': 'Total Chapters',
            'duration_seconds': 'Total Duration (s)'
        })
        print(summary)
        
    else:
        print(f"\n⚠️  No data processed. Check video files and try again.")


if __name__ == "__main__":
    main()
