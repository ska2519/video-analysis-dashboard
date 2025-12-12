# Multi-Household Video Analysis Project

## Directory Structure

```
videos/                          # Video files directory
├── household_A_day1.mp4
├── household_A_day2.mp4
├── household_A_day3.mp4
├── household_A_day4.mp4
├── household_B_day1.mp4
├── ...
└── household_F_day4.mp4

data/                            # Analysis results
├── multi_household_analysis.csv # Integrated results
└── household_summaries/         # Individual household reports
    ├── household_A_summary.json
    └── ...
```

## Usage

### 1. Batch Process All Households

```bash
# Process all 6 households, all 4 days
python batch_analysis.py

# Process specific households
python batch_analysis.py --households A B C

# Process specific days
python batch_analysis.py --days 1 2

# Custom video directory
python batch_analysis.py --video-dir /path/to/videos

# Custom output file
python batch_analysis.py --output results.csv
```

### 2. Run Dashboard

```bash
# Multi-household dashboard
streamlit run multi_household_dashboard.py

# Single household view (existing)
streamlit run chapters_app.py --server.port 8502
```

## Data Format

### multi_household_analysis.csv

| Column | Description | Example |
|--------|-------------|---------|
| household_id | Household identifier | A, B, C, D, E, F |
| day_number | Day number | 1, 2, 3, 4 |
| day_type | Weekday or weekend | weekday, weekend |
| video_id | Twelve Labs video ID | 69370feb7a1ec630b5fbdd2e |
| chapter_number | Chapter sequence | 1, 2, 3, ... |
| start_time | Start time in seconds | 36 |
| end_time | End time in seconds | 42 |
| duration_seconds | Chapter duration | 6 |
| time_of_day | Time period | morning, afternoon, evening, night |
| time_range | Formatted time | 00:36 - 00:42 |
| chapter_title | Chapter title | "Man Enters with Plates" |
| chapter_summary | Chapter description | "Man carrying two plates..." |
| timestamp | Analysis timestamp | 2025-12-12 16:03:37 |

## Next Steps

1. ✅ Create batch processing script
2. ⏳ Prepare video files (24 videos total)
3. ⏳ Run batch analysis
4. ⏳ Build multi-household dashboard
5. ⏳ Implement AI opportunity detection
