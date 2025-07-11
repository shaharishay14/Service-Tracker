# 🚗 Service Tracker Dashboard

דשבורד אינטראקטיבי לניתוח ויזואליזציה של נתוני בקשות שירות עבור חברת סיוע בדרכים.

## 📋 תיאור הפרויקט

Service Tracker הוא כלי ניתוח נתונים המיועד לעזור למנהלים ומקבלי החלטות להבין דפוסים תפעוליים כמו:

- זמני מענה לפי אזורים
- התפלגות סוגי תקלות
- מגמות נפח בקשות לאורך זמן
- מדדי ביצוע מרכזיים (KPIs)

## 🛠️ טכנולוגיות

- **Streamlit** - ממשק משתמש אינטראקטיבי
- **Pandas** - עיבוד וניתוח נתונים
- **Plotly** - ויזואליזציות אינטראקטיביות
- **Python** - שפת התכנות הראשית

## 📊 תכונות

### מדדי ביצוע מרכזיים (KPIs)

- סה"כ בקשות שירות
- זמן מענה ממוצע
- אחוז פתרון בקשות
- מספר בקשות פעילות

### ויזואליזציות

- **גרף עמודות**: זמן מענה ממוצע לפי אזור
- **גרף עוגה**: התפלגות סוגי תקלות
- **גרף קו/עמודות**: נפח בקשות לפי יום או שעה
- **מפה אינטראקטיבית**: מיקום גיאוגרפי של כל בקשות השירות

### פילטרים

- סינון לפי אזורים
- סינון לפי סוגי תקלות
- סינון לפי טווח תאריכים
- סינון לפי סטטוס בקשה

### תכונות נוספות

- טבלת נתונים מפורטת
- אפשרות הורדת נתונים כ-CSV
- **ניתוח אוטומטי עם LLM**: ניתוח חכם עם בינה מלאכותית
- **דוחות מקצועיים**: יצירת דוחות מפורטים עם המלצות
- ממשק רספונסיבי ונוח לשימוש

## 🚀 התקנה והפעלה

### דרישות מקדימות

- Python 3.8 או גרסה חדשה יותר
- pip (מנהל חבילות Python)

### שלבי התקנה

1. **שכפול הפרויקט**

   ```bash
   git clone <repository-url>
   cd service-tracker
   ```

2. **יצירת סביבה וירטואלית (מומלץ)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # או
   venv\Scripts\activate     # Windows
   ```

3. **התקנת תלויות**

   ```bash
   pip install -r requirements.txt
   ```

4. **יצירת נתוני דמה**

   ```bash
   python generate_data.py
   ```

5. **הפעלת הדשבורד**

   ```bash
   streamlit run app.py
   ```

6. **הגדרת מפתח OpenAI (אופציונלי - לניתוח מתקדם)**

   ```bash
   # הגדרת משתנה סביבה
   export OPENAI_API_KEY="your_api_key_here"

   # או הכנסת המפתח ישירות בדשבורד
   ```

7. **פתיחת הדפדפן**
   הדשבורד יפתח אוטומטית בכתובת: `http://localhost:8501`

## 📁 מבנה הפרויקט

```
service-tracker/
├── app.py                 # האפליקציה הראשית
├── generate_data.py       # סקריפט ליצירת נתוני דמה
├── service_requests.json  # קובץ נתוני בקשות השירות
├── requirements.txt       # תלויות Python
└── README.md             # תיעוד הפרויקט
```

## 📈 שימוש בדשבורד

### ניווט בממשק

1. **סרגל צד**: השתמש בפילטרים לסינון הנתונים
2. **מדדי KPI**: צפה במדדי ביצוע מרכזיים בחלק העליון
3. **גרפים**: נתח את הנתונים באמצעות ויזואליזציות אינטראקטיביות
4. **מפה גיאוגרפית**: צפה במיקום הבקשות על מפת ישראל
5. **טבלת נתונים**: צפה בנתונים המפורטים ובצע הורדה

### טיפים לשימוש

- השתמש בפילטרים כדי להתמקד באזורים או תקופות ספציפיות
- לחץ על אלמנטים בגרפים לקבלת מידע נוסף
- הורד נתונים מסוננים לניתוח נוסף ב-Excel
- השתמש בתכונת הניתוח האוטומטי לקבלת תובנות מתקדמות

### ניתוח אוטומטי עם LLM

הדשבורד כולל מערכת ניתוח חכמה המספקת:

- **ניתוח בסיסי**: ללא מפתח API - ניתוח סטטיסטי בסיסי
- **ניתוח מתקדם**: עם מפתח OpenAI - ניתוח עמוק עם GPT-4

**התכונות כוללות:**

- זיהוי אוטומטי של בעיות ואזורים בעייתיים
- המלצות מקצועיות לשיפור ביצועים
- דוח מקצועי מפורט להורדה
- תובנות עסקיות מתקדמות

## 🔧 התאמה אישית

### הוספת נתונים חדשים

1. ערוך את `generate_data.py` כדי להוסיף אזורים או סוגי תקלות
2. הרץ שוב את הסקריפט ליצירת נתונים חדשים

### שינוי עיצוב

- ערוך את `app.py` כדי לשנות צבעים, פונטים או פריסה
- השתמש ב-CSS מותאם אישית עם `st.markdown()`

### הוספת תכונות

- הוסף גרפים חדשים על ידי יצירת פונקציות נוספות
- הוסף פילטרים נוספים בפונקציה `create_sidebar_filters()`

## 🌐 פריסה (Deployment)

### Streamlit Cloud

1. העלה את הפרויקט ל-GitHub
2. התחבר ל-[Streamlit Cloud](https://streamlit.io/cloud)
3. בחר את הרפוזיטורי ופרוס את האפליקציה

### Heroku

1. צור קובץ `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. פרוס באמצעות Heroku CLI

## 🤝 תרומה לפרויקט

1. צור Fork של הפרויקט
2. צור branch חדש לתכונה שלך
3. בצע commit לשינויים
4. שלח Pull Request

## 📞 תמיכה

אם נתקלת בבעיות או יש לך שאלות:

- פתח Issue ב-GitHub
- בדוק את התיעוד של Streamlit
- צור קשר עם מפתח הפרויקט

## 📄 רישיון

פרויקט זה מופץ תחת רישיון MIT. ראה קובץ LICENSE לפרטים נוספים.

---

**Service Tracker Dashboard** - כלי חזק לניתוח נתוני שירות ושיפור ביצועים תפעוליים! 🚀
