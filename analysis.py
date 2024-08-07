def analyze_activity_sequences(va):
    sequence = extract_sequence(va)
    visits, activities = count_consecutive_groups(sequence)

    total_visits = sum(visits)
    total_activities = sum(activities)
    average_activities = calculate_averages(activities)
    average_zero_gap = calculate_gaps(activities)

    results = {
        "total_consecutive_visits": total_visits,
        "total_consecutive_activities": total_activities,
        "average_activities_in_groups": average_activities,
        "average_gaps_between_activities": average_zero_gap
    }

    return results

def extract_sequence(data):
    return [item['semanticType'] for item in data]

def count_consecutive_groups(sequence):
    last = ''
    visits = []
    activities = []
    visit_count = 0
    activity_count = 0
    
    for item in sequence:
        if item == last:
            if item == 'visit':
                visit_count += 1
            elif item == 'activity':
                activity_count += 1
        else:
            visits.append(visit_count)
            activities.append(activity_count)
            visit_count = 0
            activity_count = 0

        last = item

    visits.append(visit_count)
    activities.append(activity_count)

    return visits, activities

def calculate_averages(activities):
    non_zero_activities = [a for a in activities if a > 0]
    return sum(non_zero_activities) / len(non_zero_activities) if non_zero_activities else None

def calculate_gaps(activities):
    zero_gaps = []
    zero_count = 0

    for a in activities:
        if a == 0:
            zero_count += 1
        elif zero_count > 0:
            zero_gaps.append(zero_count)
            zero_count = 0

    if zero_count > 0:
        zero_gaps.append(zero_count)

    return sum(zero_gaps) / len(zero_gaps) if zero_gaps else None

def filter_passenger_vehicle_entries(va):
    return [entry for entry in va if entry.get('topCandidateType') == 'IN_PASSENGER_VEHICLE']