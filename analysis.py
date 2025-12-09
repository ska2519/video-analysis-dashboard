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

# === 2. Marengo: Visual Search ===
def search_marengo(query):
    """
    Search for video segments matching the query using Marengo via SDK.
    """
    try:
        # Docs: https://docs.twelvelabs.io/v1.3/sdk-reference/python/search
        # Method: client.search.query(..., query_text=..., ...)
        
        # Searching...
        # We search specifically for visual content.
        task = client.search.query(
            index_id=INDEX_ID,
            query_text=query,
            search_options=["visual"]
        )
        
        results = []
        
        # 'task' is a SyncPager object which is iterable.
        # Iterate through all pages/items.
        for item in task:
            # item is a SearchItem (or similar object)
            # Attributes: video_id, score, start, end, etc.
            
            # Client-side filtering for specific video
            if item.video_id == VIDEO_ID:
                # Handle potential None values safely
                s_stat = item.start if item.start is not None else 0.0
                e_stat = item.end if item.end is not None else 0.0
                sc_stat = item.score if item.score is not None else 0.0
                
                results.append({
                    'start': s_stat,
                    'end': e_stat,
                    'score': sc_stat
                })
                
        return results

    except Exception as e:
        print(f"Search Error (SDK): {e}")
        return []

# === 3. Pegasus: Text Generation (via Summarize) ===
def generate_pegasus(video_id, start, end, prompt):
    """
    Generate a text description using Pegasus via SDK (Summarize endpoint).
    Since 'generate' endpoint is not checking out, we use 'summarize' with specific prompt.
    """
    try:
        # SDK Usage: client.summarize(video_id, type="summary", prompt=...)
        # We inject time context into the prompt because summarize works on whole video by default.
        
        time_context_prompt = f"Based on the video segment from {start:.1f}s to {end:.1f}s, {prompt}"
        
        res = client.summarize(
            video_id=video_id,
            type="summary",
            prompt=time_context_prompt
        )
        return res.summary
    except Exception as e:
         print(f"Generation Error (SDK): {e}")
         return "Error generating text"

# === 4. Main Analysis Logic ===
def run_analysis():
    print(f"--- Starting Analysis for Video: {VIDEO_ID} ---")
    
    # 1. Search for relevant actions
    # User requested to change query to find a person
    search_query = "person" 
    print(f"1. Searching Marengo (SDK) with query: '{search_query}'...")
    
    # Note: Search in SDK might be slightly different than raw API filter.
    # Since we can't easily pass 'filter' to `search.query` in all SDK versions,
    # we'll search and then filter in python as implemented in `search_marengo`.
    search_results = search_marengo(search_query)
    
    if not search_results:
        print("No search results found (or error occurred).")
        return

    print(f"2. Found {len(search_results)} segments. Starting Pegasus analysis...")
    
    final_data = []
    
    for i, item in enumerate(search_results):
        start = item['start']
        end = item['end']
        score = item['score']
        
        print(f"   Processing segment {i+1}/{len(search_results)}: {start:.1f}s - {end:.1f}s (Score: {score:.2f})")
        
        # Pegasus Prompt
        pegasus_prompt = "describe specifically what the person is doing with the device and their body posture."
        
        # Use updated generate function
        description = generate_pegasus(VIDEO_ID, start, end, pegasus_prompt)
        
        row = {
            "video_id": VIDEO_ID,
            "start_time": start,
            "end_time": end,
            "confidence_score": score,
            "ai_description": description,
            "detected_action": "Device Interaction",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        final_data.append(row)
        
        # Rate limiting politeness
        time.sleep(1)

    # === 5. Save Results ===
    if final_data:
        df = pd.DataFrame(final_data)
        output_file = "analysis_result.csv"
        df.to_csv(output_file, index=False)
        print(f"3. Analysis complete! Results saved to '{output_file}'.")
        print(df[['start_time', 'end_time', 'ai_description']].head())

if __name__ == "__main__":
    run_analysis()
