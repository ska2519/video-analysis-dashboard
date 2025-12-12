import pandas as pd
import random
from datetime import datetime, timedelta

# Define sample data structure
households = ['A', 'B', 'C', 'D', 'E', 'F']
days = [1, 2, 3, 4]
day_types = ['weekday', 'weekday', 'weekend', 'weekend']
activities = [
    ("Morning News", "Watching morning news while drinking coffee"),
    ("Cooking", "Cooking lunch in kitchen with TV on background"),
    ("Documentary", "Sitting on sofa watching nature documentary"),
    ("Evening News", "Family watching evening news together"),
    ("Movie Night", "Family watching a movie with lights dimmed"),
    ("Phone Usage", "Watching TV while scrolling on smartphone"),
    ("Sleeping", "TV on but person appears to be sleeping on sofa")
]

data = []

# Generate random chapters for each household/day
for h in households:
    for d_idx, d in enumerate(days):
        day_type = day_types[d_idx]
        
        # Determine number of chapters for this day (random 5-15)
        num_chapters = random.randint(5, 15)
        current_time = 0 # Start of day (seconds)
        
        for i in range(1, num_chapters + 1):
            # Random duration (5 mins to 60 mins)
            duration = random.randint(300, 3600)
            start_time = current_time + random.randint(60, 600) # Gap between chapters
            end_time = start_time + duration
            current_time = end_time
            
            # Time of day logic
            hour = (start_time // 3600) % 24
            if 6 <= hour < 12: to_d = 'morning'
            elif 12 <= hour < 18: to_d = 'afternoon'
            elif 18 <= hour < 22: to_d = 'evening'
            else: to_d = 'night'
            
            # Random activity
            act_title, act_desc = random.choice(activities)
            
            # Format time range
            s_min, s_sec = divmod(start_time, 60)
            e_min, e_sec = divmod(end_time, 60)
            
            data.append({
                'household_id': h,
                'day_number': d,
                'day_type': day_type,
                'video_id': f'v_{h}_{d}',
                'chapter_number': i,
                'start_time': start_time,
                'end_time': end_time,
                'duration_seconds': duration,
                'time_of_day': to_d,
                'time_range': f"{int(s_min):02d}:{int(s_sec):02d} - {int(e_min):02d}:{int(e_sec):02d}",
                'chapter_title': f"{act_title} ({to_d})",
                'chapter_summary': f"{act_desc}. Household {h}, Day {d}.",
                'timestamp': datetime.now().isoformat()
            })

df = pd.DataFrame(data)
df.to_csv('multi_household_analysis.csv', index=False)
print(f"Generated {len(df)} sample chapters for testing.")
