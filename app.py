import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from data_analyzer import ServiceDataAnalyzer
from llm_analyzer import LLMServiceAnalyzer

# טעינת משתני סביבה מקובץ .env
load_dotenv()

# הגדרת תצורת הדף
st.set_page_config(
    page_title="Service Tracker Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """
    טוען את נתוני בקשות השירות מקובץ JSON
    
    Returns:
        pd.DataFrame: DataFrame עם נתוני בקשות השירות
    """
    try:
        with open('service_requests.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        
        # המרת עמודות התאריך לפורמט datetime
        df['opened_at'] = pd.to_datetime(df['opened_at'])
        df['responded_at'] = pd.to_datetime(df['responded_at'])
        
        # חישוב זמן מענה בדקות
        df['response_time_minutes'] = (df['responded_at'] - df['opened_at']).dt.total_seconds() / 60
        
        # הוספת עמודות נוספות לניתוח
        df['date'] = df['opened_at'].dt.date
        df['hour'] = df['opened_at'].dt.hour
        df['day_of_week'] = df['opened_at'].dt.day_name()
        
        return df
    
    except FileNotFoundError:
        st.error("קובץ service_requests.json לא נמצא. אנא הרץ את generate_data.py תחילה.")
        return pd.DataFrame()

def create_kpi_cards(df):
    """
    יוצר כרטיסי KPI (מדדי ביצוע מרכזיים)
    
    Args:
        df (pd.DataFrame): נתוני בקשות השירות
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = len(df)
        st.metric(
            label="🎫 סה״כ בקשות",
            value=total_requests
        )
    
    with col2:
        avg_response_time = df['response_time_minutes'].mean()
        st.metric(
            label="⏱️ זמן מענה ממוצע",
            value=f"{avg_response_time:.1f} דקות"
        )
    
    with col3:
        resolved_percentage = (df['status'] == 'נפתר').mean() * 100
        st.metric(
            label="✅ אחוז פתרון",
            value=f"{resolved_percentage:.1f}%"
        )
    
    with col4:
        active_requests = len(df[df['status'].isin(['בטיפול', 'ממתין'])])
        st.metric(
            label="🔄 בקשות פעילות",
            value=active_requests
        )

def create_response_time_chart(df):
    """
    יוצר גרף זמני מענה לפי אזור
    
    Args:
        df (pd.DataFrame): נתוני בקשות השירות
    
    Returns:
        plotly.graph_objects.Figure: גרף עמודות אינטראקטיבי
    """
    # חישוב זמן מענה ממוצע לפי אזור
    avg_response_by_region = df.groupby('region')['response_time_minutes'].mean().sort_values(ascending=True)
    
    fig = px.bar(
        x=avg_response_by_region.values,
        y=avg_response_by_region.index,
        orientation='h',
        title="זמן מענה ממוצע לפי אזור (בדקות)",
        labels={'x': 'זמן מענה ממוצע (דקות)', 'y': 'אזור'},
        color=avg_response_by_region.values,
        color_continuous_scale='RdYlGn_r'  # צבעים: אדום לירוק הפוך
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        font=dict(size=12)
    )
    
    return fig

def create_issue_distribution_chart(df):
    """
    יוצר גרף התפלגות סוגי תקלות
    
    Args:
        df (pd.DataFrame): נתוני בקשות השירות
    
    Returns:
        plotly.graph_objects.Figure: גרף עוגה אינטראקטיבי
    """
    issue_counts = df['issue_type'].value_counts()
    
    fig = px.pie(
        values=issue_counts.values,
        names=issue_counts.index,
        title="התפלגות סוגי תקלות"
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>כמות: %{value}<br>אחוז: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        font=dict(size=12)
    )
    
    return fig

def create_volume_chart(df, time_unit='day'):
    """
    יוצר גרף נפח בקשות לאורך זמן
    
    Args:
        df (pd.DataFrame): נתוני בקשות השירות
        time_unit (str): יחידת זמן - 'day' או 'hour'
    
    Returns:
        plotly.graph_objects.Figure: גרף קו או עמודות
    """
    if time_unit == 'day':
        volume_data = df.groupby('date').size().reset_index(name='count')
        volume_data['date'] = pd.to_datetime(volume_data['date'])
        
        fig = px.line(
            volume_data,
            x='date',
            y='count',
            title="נפח בקשות שירות לפי יום",
            labels={'date': 'תאריך', 'count': 'מספר בקשות'}
        )
        
    else:  # hour
        volume_data = df.groupby('hour').size().reset_index(name='count')
        
        fig = px.bar(
            volume_data,
            x='hour',
            y='count',
            title="נפח בקשות שירות לפי שעה ביום",
            labels={'hour': 'שעה', 'count': 'מספר בקשות'}
        )
    
    fig.update_layout(
        height=400,
        font=dict(size=12)
    )
    
    return fig

def create_map_visualization(df):
    """
    יוצר מפה אינטראקטיבית המציגה את מיקומי בקשות השירות
    
    Args:
        df (pd.DataFrame): נתוני בקשות השירות עם קואורדינטות
    
    Returns:
        plotly.graph_objects.Figure: מפה אינטראקטיבית
    """
    # יצירת צבעים לפי סוג תקלה
    color_map = {
        'בטריה': '#FF6B6B',
        'פנצ\'ר': '#4ECDC4', 
        'תקלת מנוע': '#45B7D1',
        'נגמר דלק': '#96CEB4',
        'מפתח נעול ברכב': '#FFEAA7',
        'תקלת חשמל': '#DDA0DD',
        'תאונה קלה': '#FFB347'
    }
    
    # הכנת הנתונים למפה
    df_map = df.copy()
    df_map['color'] = df_map['issue_type'].map(color_map)
    df_map['size'] = df_map['response_time_minutes'].apply(lambda x: max(8, min(20, x/10)))  # גודל לפי זמן מענה
    
    # יצירת טקסט hover מפורט
    df_map['hover_text'] = (
        '<b>' + df_map['id'] + '</b><br>' +
        'אזור: ' + df_map['region'] + '<br>' +
        'סוג תקלה: ' + df_map['issue_type'] + '<br>' +
        'סטטוס: ' + df_map['status'] + '<br>' +
        'זמן מענה: ' + df_map['response_time_minutes'].round(1).astype(str) + ' דקות<br>' +
        'נפתח: ' + df_map['opened_at'].dt.strftime('%d/%m/%Y %H:%M')
    )
    
    fig = px.scatter_mapbox(
        df_map,
        lat='latitude',
        lon='longitude',
        color='issue_type',
        size='size',
        hover_name='id',
        hover_data={
            'region': True,
            'issue_type': True,
            'status': True,
            'response_time_minutes': ':.1f',
            'latitude': False,
            'longitude': False,
            'size': False
        },
        color_discrete_map=color_map,
        title="מפת בקשות שירות - מיקום גיאוגרפי",
        mapbox_style="open-street-map",
        zoom=7,
        center={"lat": 31.5, "lon": 34.8},  # מרכז ישראל
        height=600
    )
    
    fig.update_layout(
        font=dict(size=12),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig

def create_sidebar_filters(df):
    """
    יוצר פילטרים בסרגל הצד
    
    Args:
        df (pd.DataFrame): נתוני בקשות השירות
    
    Returns:
        tuple: (filtered_df, selected_regions, selected_issues, date_range)
    """
    st.sidebar.header("🔍 פילטרים")
    
    # פילטר אזורים
    all_regions = df['region'].unique().tolist()
    selected_regions = st.sidebar.multiselect(
        "בחר אזורים:",
        options=all_regions,
        default=all_regions
    )
    
    # פילטר סוגי תקלות
    all_issues = df['issue_type'].unique().tolist()
    selected_issues = st.sidebar.multiselect(
        "בחר סוגי תקלות:",
        options=all_issues,
        default=all_issues
    )
    
    # פילטר טווח תאריכים
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    date_range = st.sidebar.date_input(
        "בחר טווח תאריכים:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # פילטר סטטוס
    all_statuses = df['status'].unique().tolist()
    selected_statuses = st.sidebar.multiselect(
        "בחר סטטוסים:",
        options=all_statuses,
        default=all_statuses
    )
    
    # החלת הפילטרים
    filtered_df = df[
        (df['region'].isin(selected_regions)) &
        (df['issue_type'].isin(selected_issues)) &
        (df['status'].isin(selected_statuses))
    ]
    
    # פילטר תאריכים
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date'] >= start_date) &
            (filtered_df['date'] <= end_date)
        ]
    
    return filtered_df, selected_regions, selected_issues, date_range

def main():
    """
    הפונקציה הראשית של האפליקציה
    """
    # כותרת ראשית
    st.title("🚗 Service Tracker Dashboard")
    st.markdown("**דשבורד לניתוח בקשות שירות - חברת סיוע בדרכים**")
    st.markdown("---")
    
    # טעינת נתונים
    df = load_data()
    
    if df.empty:
        st.stop()
    
    # יצירת פילטרים
    filtered_df, selected_regions, selected_issues, date_range = create_sidebar_filters(df)
    
    # הצגת מידע על הפילטרים הפעילים
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**מציג {len(filtered_df)} מתוך {len(df)} בקשות**")
    
    # כרטיסי KPI
    st.subheader("📊 מדדי ביצוע מרכזיים")
    create_kpi_cards(filtered_df)
    
    st.markdown("---")
    
    # גרפים ראשיים
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_response_time_chart(filtered_df),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_issue_distribution_chart(filtered_df),
            use_container_width=True
        )
    
    # גרף נפח בקשות
    st.subheader("📈 ניתוח נפח בקשות")
    
    # בחירת יחידת זמן
    time_unit = st.radio(
        "בחר יחידת זמן:",
        options=['day', 'hour'],
        format_func=lambda x: 'לפי יום' if x == 'day' else 'לפי שעה',
        horizontal=True
    )
    
    st.plotly_chart(
        create_volume_chart(filtered_df, time_unit),
        use_container_width=True
    )
    
    # מפה גיאוגרפית
    st.subheader("🗺️ מפת בקשות שירות")
    
    # בדיקה אם יש נתוני קואורדינטות
    if 'latitude' in filtered_df.columns and 'longitude' in filtered_df.columns:
        st.plotly_chart(
            create_map_visualization(filtered_df),
            use_container_width=True
        )
        
        # הסבר על המפה
        st.info("""
        **הסבר על המפה:**
        - כל נקודה מייצגת בקשת שירות
        - צבע הנקודה מציין את סוג התקלה
        - גודל הנקודה מציין את זמן המענה (גדול יותר = זמן מענה ארוך יותר)
        - לחץ על נקודה לקבלת פרטים מלאים
        """)
    else:
        st.warning("נתוני קואורדינטות לא זמינים. אנא הרץ את generate_data.py מחדש ליצירת נתונים עם מיקומים.")
    
    # טבלת נתונים מפורטת
    st.subheader("📋 נתונים מפורטים")
    
    # הצגת הנתונים המסוננים
    columns_to_show = ['id', 'opened_at', 'responded_at', 'region', 'issue_type', 'status', 'response_time_minutes']
    
    # הוספת קואורדינטות אם קיימות
    if 'latitude' in filtered_df.columns and 'longitude' in filtered_df.columns:
        columns_to_show.extend(['latitude', 'longitude'])
    
    display_df = filtered_df[columns_to_show].copy()
    display_df['response_time_minutes'] = display_df['response_time_minutes'].round(1)
    
    # שינוי שמות העמודות לעברית
    column_names = ['מזהה', 'זמן פתיחה', 'זמן מענה', 'אזור', 'סוג תקלה', 'סטטוס', 'זמן מענה (דקות)']
    if 'latitude' in filtered_df.columns and 'longitude' in filtered_df.columns:
        column_names.extend(['קו רוחב', 'קו אורך'])
    
    display_df.columns = column_names
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # אפשרות להורדת הנתונים
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 הורד נתונים כ-CSV",
        data=csv,
        file_name=f"service_requests_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # ניתוח אוטומטי עם LLM
    st.markdown("---")
    st.subheader("🤖 ניתוח אוטומטי ומסקנות")
    
    st.info("""
    **ניתוח חכם עם בינה מלאכותית**
    
    לחץ על הכפתור למטה כדי לקבל ניתוח מקצועי של הנתונים עם:
    - זיהוי בעיות ואזורים בעייתיים
    - המלצות לשיפור ביצועים
    - תובנות עסקיות מתקדמות
    - דוח מקצועי להורדה
    """)
    
    # בדיקה אם יש מפתח API בקובץ .env
    env_api_key = os.getenv('OPENAI_API_KEY')
    
    # הגדרת מפתח API ומודל
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if env_api_key:
            st.success("✅ **מפתח OpenAI API נמצא בקובץ .env**")
            # הצגת חלק מהמפתח (מוסווה) לאימות
            masked_key = env_api_key[:8] + "..." + env_api_key[-4:] if len(env_api_key) > 12 else "***"
            st.info(f"המערכת תשתמש במפתח: `{masked_key}`")
            api_key = env_api_key
            # אפשרות לעקוף את המפתח מהקובץ
            override_key = st.text_input(
                "עקוף מפתח (אופציונלי)",
                type="password",
                help="השאר ריק כדי להשתמש במפתח מקובץ ה-.env"
            )
            if override_key.strip():
                api_key = override_key
                st.warning("⚠️ משתמש במפתח שהוכנס במקום זה שבקובץ .env")
        else:
            api_key = st.text_input(
                "מפתח OpenAI API (אופציונלי - לניתוח מתקדם)",
                type="password",
                help="הכנס מפתח OpenAI API לקבלת ניתוח מתקדם. ללא מפתח תקבל ניתוח בסיסי."
            )
            
            # הודעה על אפשרות שימוש בקובץ .env
            with st.expander("💡 טיפ: שימוש בקובץ .env"):
                st.markdown("""
                **לשימוש קבוע, מומלץ ליצור קובץ `.env` בתיקיית הפרויקט:**
                
                1. צור קובץ בשם `.env` (ללא סיומת)
                2. הוסף את השורה הבאה:
                ```
                OPENAI_API_KEY=sk-your-api-key-here
                ```
                3. הפעל מחדש את האפליקציה
                
                **יתרונות:**
                - המפתח נשמר באופן קבוע
                - לא צריך להכניס אותו בכל פעם
                - בטוח יותר (הקובץ לא נשלח ל-Git)
                """)
                
                if st.button("📁 צור קובץ .env לדוגמה"):
                    env_content = "# הכנס את מפתח OpenAI API שלך כאן\nOPENAI_API_KEY=sk-your-api-key-here\n"
                    st.download_button(
                        label="💾 הורד קובץ .env לדוגמה",
                        data=env_content,
                        file_name=".env",
                        mime="text/plain"
                    )
    
    with col2:
        model_options = {
            "gpt-4": "GPT-4 (מומלץ)",
            "gpt-4-turbo": "GPT-4 Turbo",
            "gpt-3.5-turbo": "GPT-3.5 Turbo (זול יותר)"
        }
        
        selected_model = st.selectbox(
            "בחר מודל AI:",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            help="GPT-4 מספק ניתוח מעמיק יותר אך יקר יותר. GPT-3.5 מהיר וחסכוני."
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)  # רווח
        analyze_button = st.button(
            "🔍 נתח נתונים",
            type="primary",
            use_container_width=True
        )
    
    # ביצוע הניתוח
    if analyze_button:
        # הצגת מידע על המודל שנבחר
        if api_key:
            if env_api_key and api_key == env_api_key:
                st.info(f"🤖 משתמש במודל: {model_options[selected_model]} (מפתח מקובץ .env)")
            else:
                st.info(f"🤖 משתמש במודל: {model_options[selected_model]} (מפתח שהוכנס)")
        else:
            st.info("🤖 משתמש בניתוח בסיסי (ללא API)")
            
        with st.spinner("מנתח נתונים ויוצר דוח מקצועי..."):
            try:
                # יצירת מנתח הנתונים
                data_analyzer = ServiceDataAnalyzer(filtered_df)
                analysis_data = data_analyzer.generate_comprehensive_analysis()
                
                # יצירת מנתח LLM
                llm_analyzer = LLMServiceAnalyzer(
                    api_key=api_key if api_key else None,
                    model=selected_model
                )
                
                # ביצוע הניתוח
                llm_result = llm_analyzer.analyze_with_llm(analysis_data)
                
                # הצגת התוצאות
                st.success("הניתוח הושלם בהצלחה!")
                
                # הצגת מידע על סוג הניתוח
                if llm_result['api_used']:
                    st.success(f"✅ **ניתוח מתקדם עם AI הושלם!**")
                    st.info(f"🤖 **מודל שנוצל:** {llm_result['model_used']}")
                    if llm_result.get('tokens_used'):
                        st.info(f"🔢 **טוקנים שנוצלו:** {llm_result['tokens_used']}")
                else:
                    if llm_result['analysis_type'] == 'basic_fallback':
                        st.warning("⚠️ **נכשל בחיבור ל-API - מציג ניתוח בסיסי**")
                        if llm_result.get('error'):
                            st.error(f"שגיאה: {llm_result['error']}")
                    elif llm_result['analysis_type'] == 'basic_invalid_key':
                        st.warning("⚠️ **מפתח API לא תקין - מציג ניתוח בסיסי**")
                        st.info("💡 וודא שהמפתח מתחיל ב-'sk-' ומכיל לפחות 10 תווים")
                    else:
                        st.info("ℹ️ **ניתוח בסיסי (ללא API)**")
                
                # הצגת הניתוח
                st.markdown("### 📊 תוצאות הניתוח")
                st.markdown(llm_result['analysis'])
                
                # יצירת קובץ דוח להורדה
                report_content = llm_analyzer.generate_report_file(analysis_data, llm_result)
                
                # כפתור הורדת הדוח
                st.download_button(
                    label="📄 הורד דוח מקצועי",
                    data=report_content,
                    file_name=f"service_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    help="הורד דוח מקצועי מלא עם כל הניתוחים והמלצות"
                )
                
                # הצגת תובנות מרכזיות
                st.markdown("### 💡 תובנות מרכזיות")
                key_insights = data_analyzer.get_key_insights()
                for i, insight in enumerate(key_insights, 1):
                    st.write(f"{i}. {insight}")
                
            except Exception as e:
                st.error(f"שגיאה בניתוח הנתונים: {str(e)}")
                st.info("נסה שוב או בדוק את מפתח ה-API")

if __name__ == "__main__":
    main() 