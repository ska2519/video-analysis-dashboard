"""
Test the batch analysis workflow with existing video data
"""

import os
import shutil
from pathlib import Path

# Create sample structure using existing video
print("Setting up test environment...")

# Check if we have the existing video
existing_video = "path_to_existing_video.mp4"  # Replace with actual path if available

# For now, create a note about video preparation
videos_dir = Path("videos")
videos_dir.mkdir(exist_ok=True)

readme_content = """
# Video Files Setup

## Required Structure

Place your video files in this directory with the following naming convention:

```
household_A_day1.mp4
household_A_day2.mp4
household_A_day3.mp4
household_A_day4.mp4
household_B_day1.mp4
household_B_day2.mp4
household_B_day3.mp4
household_B_day4.mp4
household_C_day1.mp4
...
household_F_day4.mp4
```

## Total Files Needed

- 6 households (A-F)
- 4 days each
- **Total: 24 video files**

## File Format

- Format: MP4
- Duration: Up to 24 hours per file (Twelve Labs supports up to 1 hour, so may need to split)
- Language: English audio (for transcription)

## Current Status

- [ ] Household A videos (0/4)
- [ ] Household B videos (0/4)
- [ ] Household C videos (0/4)
- [ ] Household D videos (0/4)
- [ ] Household E videos (0/4)
- [ ] Household F videos (0/4)

## Testing with Sample Data

For testing, you can:
1. Use the existing video as household_A_day1.mp4
2. Run: `python batch_analysis.py --households A --days 1`
3. View results: `streamlit run multi_household_dashboard.py`
"""

with open(videos_dir / "README.md", "w") as f:
    f.write(readme_content)

print(f"✓ Created {videos_dir}/README.md")
print("\nNext steps:")
print("1. Place video files in the 'videos' directory")
print("2. Run: python batch_analysis.py --households A --days 1  (for testing)")
print("3. Run: streamlit run multi_household_dashboard.py")
