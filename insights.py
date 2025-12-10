import pandas as pd
import re

def normalize_text(text):
    return text.lower().strip()

def identify_entity(description):
    """
    Classifies the description into a specific Actor/Entity based on keywords.
    Returns: (Entity Name, Icon)
    """
    desc = normalize_text(description)
    
    # Actor A: Man in Black Jacket (The Worker/Staff)
    if "black jacket" in desc and ("plate" in desc or "man" in desc):
        return "Staff (Black Jacket)", "👨‍💼"
    
    # Actor B: Person in Hoodie (Delivery)
    if "hoodie" in desc and ("white bag" in desc or "bag" in desc):
        return "Delivery (Hoodie)", "🚚"
    
    # Actor C: Phone Case Person (Visitor)
    if "phone case" in desc:
        return "Visitor (Phone)", "📱"
        
    return "Unknown", "❓"

def deduplicate_events(df, time_threshold=5.0):
    """
    Merges overlapping or consecutive events that belong to the same entity.
    """
    if df.empty:
        return df
        
    # Ensure sorted
    df = df.sort_values('start_time').reset_index(drop=True)
    
    merged_events = []
    current_event = None
    
    for _, row in df.iterrows():
        entity_name, entity_icon = identify_entity(row['ai_description'])
        
        # Create a structured object for the current row
        row_data = {
            'start_time': row['start_time'],
            'end_time': row['end_time'],
            'ai_description': row['ai_description'],
            'entity': entity_name,
            'icon': entity_icon,
            'original_count': 1
        }
        
        if current_event is None:
            current_event = row_data
            continue
            
        # Check for merge criteria
        # 1. Same Entity
        # 2. Time proximity (Start time of new event is close to end time of old event)
        time_gap = row_data['start_time'] - current_event['end_time']
        
        if (row_data['entity'] == current_event['entity']) and (row_data['entity'] != "Unknown") and (time_gap < time_threshold):
            # MERGE
            current_event['end_time'] = max(current_event['end_time'], row_data['end_time'])
            current_event['ai_description'] += " | " + row_data['ai_description'] # Concatenate descriptions for now
            current_event['original_count'] += 1
        else:
            # PUSH & RESET
            merged_events.append(current_event)
            current_event = row_data
            
    if current_event:
        merged_events.append(current_event)
        
    # Convert back to DataFrame
    result_df = pd.DataFrame(merged_events)
    
    # Cleanup Description (Take the first sentence of the first unique description to avoid massive blobs)
    # Or maybe keep it simple for now
    result_df['Duration'] = result_df['end_time'] - result_df['start_time']
    
    # Format times for display
    def format_time(seconds):
        m, s = divmod(float(seconds), 60)
        return f"{int(m):02d}:{int(s):02d}"

    result_df['Start'] = result_df['start_time'].apply(format_time)
    result_df['End'] = result_df['end_time'].apply(format_time)
        
    return result_df
