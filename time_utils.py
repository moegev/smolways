from datetime import datetime

def find_min_max_dates(va):
    if not va:
        return None, None
    
    min_date_str = va[0].get('startTime')
    max_date_str = va[-1].get('endTime')
    
    min_date = datetime.fromisoformat(min_date_str) if min_date_str else None
    max_date = datetime.fromisoformat(max_date_str) if max_date_str else None
    
    return min_date, max_date

def format_datetime_info(datetime_str):
    dt = datetime.fromisoformat(datetime_str)
    day_of_week = dt.strftime('%A')
    date = dt.strftime('%Y-%m-%d')
    time = dt.strftime('%H:%M')  # 24-hour format
    return day_of_week, date, time

def get_day_of_week(date_str):
    date_obj = datetime.fromisoformat(date_str)
    return date_obj.strftime('%A')

def calculate_duration(start_time_str, end_time_str):
    start_time = datetime.fromisoformat(start_time_str)
    end_time = datetime.fromisoformat(end_time_str)
    duration = end_time - start_time
    return int(duration.total_seconds())

def count_unique_drive_days(passenger_va):
    unique_days = set()
    for entry in passenger_va:
        start_time_str = entry.get('startTime')
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str)
            start_date = start_time.date()
            unique_days.add(start_date)
    return len(unique_days)