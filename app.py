import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

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
    
    # טבלת נתונים מפורטת
    st.subheader("📋 נתונים מפורטים")
    
    # הצגת הנתונים המסוננים
    display_df = filtered_df[['id', 'opened_at', 'responded_at', 'region', 'issue_type', 'status', 'response_time_minutes']].copy()
    display_df['response_time_minutes'] = display_df['response_time_minutes'].round(1)
    
    # שינוי שמות העמודות לעברית
    display_df.columns = ['מזהה', 'זמן פתיחה', 'זמן מענה', 'אזור', 'סוג תקלה', 'סטטוס', 'זמן מענה (דקות)']
    
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

if __name__ == "__main__":
    main() 