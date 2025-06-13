import json
import random
from datetime import datetime, timedelta

def generate_service_requests(num_records=100):
    """
    יוצר נתוני דמה עבור בקשות שירות
    
    Args:
        num_records (int): מספר הרשומות ליצירה
    
    Returns:
        list: רשימת בקשות שירות
    """
    
    # רשימת אזורים בישראל עם קואורדינטות
    regions_data = {
        "תל אביב": {"lat": 32.0853, "lon": 34.7818},
        "חיפה": {"lat": 32.7940, "lon": 34.9896},
        "ירושלים": {"lat": 31.7683, "lon": 35.2137},
        "באר שבע": {"lat": 31.2518, "lon": 34.7915},
        "נתניה": {"lat": 32.3215, "lon": 34.8532},
        "פתח תקווה": {"lat": 32.0870, "lon": 34.8873},
        "אשדוד": {"lat": 31.8044, "lon": 34.6553},
        "ראשון לציון": {"lat": 31.9730, "lon": 34.8066}
    }
    regions = list(regions_data.keys())
    
    # סוגי תקלות נפוצות
    issue_types = ["מצבר", "פנצ'ר", "תקלת מנוע", "נגמר דלק", "מפתח נעול ברכב", "תקלת חשמל", "תאונה קלה"]
    
    # סטטוסים אפשריים
    statuses = ["נפתר", "בטיפול", "ממתין", "בוטל"]
    
    service_requests = []
    
    # יצירת תאריך התחלה (30 ימים אחורה)
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_records):
        # יצירת מזהה ייחודי
        request_id = f"REQ{str(i+1).zfill(3)}"
        
        # יצירת זמן פתיחת הבקשה (רנדומלי ב-30 הימים האחרונים)
        opened_at = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(6, 22),  # שעות עבודה בעיקר
            minutes=random.randint(0, 59)
        )
        
        # יצירת זמן מענה (בין 10 דקות ל-3 שעות אחרי הפתיחה)
        response_delay = timedelta(
            minutes=random.randint(10, 180)
        )
        responded_at = opened_at + response_delay
        
        # בחירת נתונים רנדומליים
        region = random.choice(regions)
        issue_type = random.choice(issue_types)
        status = random.choice(statuses)
        
        # הוספת רעש קטן לקואורדינטות (כדי לא להציג את כל הנקודות באותו מקום)
        base_lat = regions_data[region]["lat"]
        base_lon = regions_data[region]["lon"]
        lat = base_lat + random.uniform(-0.05, 0.05)  # רעש של עד 5 ק"מ
        lon = base_lon + random.uniform(-0.05, 0.05)
        
        # יצירת רשומת בקשת שירות
        request = {
            "id": request_id,
            "opened_at": opened_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "responded_at": responded_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "region": region,
            "issue_type": issue_type,
            "status": status,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6)
        }
        
        service_requests.append(request)
    
    return service_requests

def save_to_json(data, filename="service_requests.json"):
    """
    שומר את הנתונים לקובץ JSON
    
    Args:
        data (list): רשימת בקשות השירות
        filename (str): שם הקובץ לשמירה
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"נוצרו {len(data)} רשומות ונשמרו בקובץ {filename}")

if __name__ == "__main__":
    # יצירת 100 רשומות דמה
    requests = generate_service_requests(100)
    
    # שמירה לקובץ JSON
    save_to_json(requests)
    
    # הדפסת דוגמה
    print("\nדוגמה לרשומה:")
    print(json.dumps(requests[0], ensure_ascii=False, indent=2)) 