import json
from datetime import datetime
import pandas as pd
import numpy as np
from time_utils import get_day_of_week, calculate_duration

def load_json_data(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{filename}' is not a valid JSON file.")
    return None

def process_data(data):
    visits_activities = []
    timelinePaths = []
    for item in data["semanticSegments"]:
        if is_after(item["startTime"], "2024-02-01T06:00:00-07:00"):
            if item.get('timelinePath') is not None:
                timelinePaths.append(item)
            if item.get("activity") is not None:   
                visits_activities.append(flatten_activity(item))
            if item.get("visit") is not None:  
                visits_activities.append(flatten_visit(item))
    print("\nAnalyzed Google Timeline Data")
    print("  Total Events:", len(visits_activities))
    print("  Total timelinePaths:", len(timelinePaths))
    return visits_activities, timelinePaths

def is_after(date_str, compare_str):
    date_time = datetime.fromisoformat(date_str)
    compare_time = datetime.fromisoformat(compare_str)
    return date_time > compare_time

def flatten_activity(activity_dict):
    start_time = activity_dict.get('startTime')
    end_time = activity_dict.get('endTime')
    start_time_offset = activity_dict.get('startTimeTimezoneUtcOffsetMinutes', np.nan)
    end_time_offset = activity_dict.get('endTimeTimezoneUtcOffsetMinutes', np.nan)

    activity = activity_dict.get('activity', {})
    start_lat_lng = activity.get('start', {}).get('latLng', np.nan)
    end_lat_lng = activity.get('end', {}).get('latLng', np.nan)
    distance_meters = activity.get('distanceMeters', np.nan)
    activity_probability = activity.get('probability', np.nan)

    top_candidate = activity.get('topCandidate', {})
    top_candidate_type = top_candidate.get('type', np.nan)
    top_candidate_probability = top_candidate.get('probability', np.nan)

    parking = activity.get('parking', {})
    parking_lat_lng = parking.get('location', {}).get('latLng', np.nan)
    parking_start_time = parking.get('startTime', np.nan)

    return {
        'semanticType': 'activity',
        'startTime': start_time,
        'endTime': end_time,
        'startTimeTimezoneUtcOffsetMinutes': start_time_offset,
        'endTimeTimezoneUtcOffsetMinutes': end_time_offset,
        'startLatLng': start_lat_lng,
        'endLatLng': end_lat_lng,
        'distanceMeters': distance_meters,
        'activityProbability': activity_probability,
        'topCandidateType': top_candidate_type,
        'topCandidateProbability': top_candidate_probability,
        'parkingLatLng': parking_lat_lng,
        'parkingStartTime': parking_start_time
    }

def flatten_visit(visit_dict):
    start_time = visit_dict.get('startTime')
    end_time = visit_dict.get('endTime')
    start_time_offset = visit_dict.get('startTimeTimezoneUtcOffsetMinutes', np.nan)
    end_time_offset = visit_dict.get('endTimeTimezoneUtcOffsetMinutes', np.nan)

    visit = visit_dict.get('visit', {})
    hierarchy_level = visit.get('hierarchyLevel', np.nan)
    visit_probability = visit.get('probability', np.nan)

    top_candidate = visit.get('topCandidate', {})
    place_id = top_candidate.get('placeId', np.nan)
    semantic_type = top_candidate.get('semanticType', np.nan)
    top_candidate_probability = top_candidate.get('probability', np.nan)
    place_lat_lng = top_candidate.get('placeLocation', {}).get('latLng', np.nan)

    return {
        'semanticType': 'visit',
        'startTime': start_time,
        'endTime': end_time,
        'startTimeTimezoneUtcOffsetMinutes': start_time_offset,
        'endTimeTimezoneUtcOffsetMinutes': end_time_offset,
        'hierarchyLevel': hierarchy_level,
        'visitProbability': visit_probability,
        'placeId': place_id,
        'semanticType': semantic_type,
        'topCandidateProbability': top_candidate_probability,
        'placeLatLng': place_lat_lng
    }

def add_duration_to_va(va):
    for entry in va:
        start_time = entry.get('startTime')
        end_time = entry.get('endTime')

        if start_time:
            entry['day-of-week'] = get_day_of_week(start_time)

        if start_time and end_time:
            seconds = calculate_duration(start_time, end_time)
            entry['duration'] = seconds

    return va

def check_missing_times(va):
    missing_times_indices = []
    for index, entry in enumerate(va):
        start_time = entry.get('startTime')
        end_time = entry.get('endTime')

        if start_time is None or end_time is None or \
           (isinstance(start_time, float) and np.isnan(start_time)) or \
           (isinstance(end_time, float) and np.isnan(end_time)):
            missing_times_indices.append(index)
    
    print(f"{len(missing_times_indices)} items missing start/end")
    return missing_times_indices