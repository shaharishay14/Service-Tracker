import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple

class ServiceDataAnalyzer:
    """
    מחלקה לניתוח נתוני בקשות שירות והפקת תובנות עסקיות
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        אתחול המנתח עם DataFrame של נתוני בקשות השירות
        
        Args:
            df (pd.DataFrame): נתוני בקשות השירות
        """
        self.df = df.copy()
        self.analysis_results = {}
    
    def analyze_response_times(self) -> Dict:
        """
        ניתוח זמני מענה לפי אזורים וסוגי תקלות
        
        Returns:
            Dict: תוצאות ניתוח זמני המענה
        """
        # ניתוח לפי אזורים
        region_stats = self.df.groupby('region')['response_time_minutes'].agg([
            'mean', 'median', 'std', 'min', 'max', 'count'
        ]).round(2)
        
        # ניתוח לפי סוגי תקלות
        issue_stats = self.df.groupby('issue_type')['response_time_minutes'].agg([
            'mean', 'median', 'std', 'min', 'max', 'count'
        ]).round(2)
        
        # זיהוי אזורים בעייתיים (זמן מענה גבוה)
        avg_response_time = self.df['response_time_minutes'].mean()
        problematic_regions = region_stats[region_stats['mean'] > avg_response_time * 1.2]
        
        # זיהוי תקלות מורכבות (זמן מענה ארוך)
        complex_issues = issue_stats[issue_stats['mean'] > avg_response_time * 1.1]
        
        return {
            'overall_avg': round(avg_response_time, 2),
            'region_stats': region_stats.to_dict('index'),
            'issue_stats': issue_stats.to_dict('index'),
            'problematic_regions': problematic_regions.to_dict('index'),
            'complex_issues': complex_issues.to_dict('index')
        }
    
    def analyze_volume_patterns(self) -> Dict:
        """
        ניתוח דפוסי נפח בקשות לפי זמן
        
        Returns:
            Dict: תוצאות ניתוח דפוסי הנפח
        """
        # ניתוח לפי שעות
        hourly_volume = self.df.groupby('hour').size()
        peak_hours = hourly_volume.nlargest(3)
        quiet_hours = hourly_volume.nsmallest(3)
        
        # ניתוח לפי ימי השבוע
        daily_volume = self.df.groupby('day_of_week').size()
        busiest_days = daily_volume.nlargest(3)
        
        # ניתוח לפי תאריכים
        date_volume = self.df.groupby('date').size()
        busiest_dates = date_volume.nlargest(5)
        
        return {
            'total_requests': len(self.df),
            'avg_daily_requests': round(date_volume.mean(), 1),
            'peak_hours': peak_hours.to_dict(),
            'quiet_hours': quiet_hours.to_dict(),
            'busiest_days': busiest_days.to_dict(),
            'busiest_dates': busiest_dates.to_dict()
        }
    
    def analyze_issue_distribution(self) -> Dict:
        """
        ניתוח התפלגות סוגי תקלות
        
        Returns:
            Dict: תוצאות ניתוח התפלגות התקלות
        """
        issue_counts = self.df['issue_type'].value_counts()
        issue_percentages = (issue_counts / len(self.df) * 100).round(1)
        
        # ניתוח לפי אזורים
        region_issue_matrix = pd.crosstab(self.df['region'], self.df['issue_type'])
        
        return {
            'issue_counts': issue_counts.to_dict(),
            'issue_percentages': issue_percentages.to_dict(),
            'most_common_issue': issue_counts.index[0],
            'least_common_issue': issue_counts.index[-1],
            'region_issue_matrix': region_issue_matrix.to_dict('index')
        }
    
    def analyze_status_performance(self) -> Dict:
        """
        ניתוח ביצועי פתרון בקשות
        
        Returns:
            Dict: תוצאות ניתוח ביצועי הפתרון
        """
        status_counts = self.df['status'].value_counts()
        status_percentages = (status_counts / len(self.df) * 100).round(1)
        
        # ניתוח זמני מענה לפי סטטוס
        status_response_times = self.df.groupby('status')['response_time_minutes'].mean().round(2)
        
        # חישוב אחוז פתרון
        resolved_rate = (status_counts.get('נפתר', 0) / len(self.df) * 100)
        
        return {
            'status_counts': status_counts.to_dict(),
            'status_percentages': status_percentages.to_dict(),
            'resolved_rate': round(resolved_rate, 1),
            'status_response_times': status_response_times.to_dict()
        }
    
    def identify_geographic_patterns(self) -> Dict:
        """
        זיהוי דפוסים גיאוגרפיים
        
        Returns:
            Dict: תוצאות ניתוח גיאוגרפי
        """
        if 'latitude' not in self.df.columns or 'longitude' not in self.df.columns:
            return {'error': 'נתוני קואורדינטות לא זמינים'}
        
        # ניתוח לפי אזורים
        region_analysis = self.df.groupby('region').agg({
            'response_time_minutes': ['mean', 'count'],
            'latitude': 'mean',
            'longitude': 'mean'
        }).round(4)
        
        region_analysis.columns = ['avg_response_time', 'request_count', 'center_lat', 'center_lon']
        
        # זיהוי אזורי ריכוז
        high_volume_regions = region_analysis[region_analysis['request_count'] > region_analysis['request_count'].mean()]
        
        return {
            'region_analysis': region_analysis.to_dict('index'),
            'high_volume_regions': high_volume_regions.to_dict('index')
        }
    
    def generate_comprehensive_analysis(self) -> Dict:
        """
        יצירת ניתוח מקיף של כל הנתונים
        
        Returns:
            Dict: ניתוח מקיף עם כל התובנות
        """
        analysis = {
            'metadata': {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_records': len(self.df),
                'date_range': {
                    'start': self.df['opened_at'].min().strftime('%Y-%m-%d'),
                    'end': self.df['opened_at'].max().strftime('%Y-%m-%d')
                }
            },
            'response_times': self.analyze_response_times(),
            'volume_patterns': self.analyze_volume_patterns(),
            'issue_distribution': self.analyze_issue_distribution(),
            'status_performance': self.analyze_status_performance(),
            'geographic_patterns': self.identify_geographic_patterns()
        }
        
        self.analysis_results = analysis
        return analysis
    
    def get_key_insights(self) -> List[str]:
        """
        חילוץ תובנות מרכזיות מהניתוח
        
        Returns:
            List[str]: רשימת תובנות מרכזיות
        """
        if not self.analysis_results:
            self.generate_comprehensive_analysis()
        
        insights = []
        
        # תובנות זמני מענה
        response_data = self.analysis_results['response_times']
        insights.append(f"זמן מענה ממוצע כללי: {response_data['overall_avg']} דקות")
        
        if response_data['problematic_regions']:
            worst_region = max(response_data['problematic_regions'].items(), 
                             key=lambda x: x[1]['mean'])
            insights.append(f"אזור עם זמן מענה הגבוה ביותר: {worst_region[0]} ({worst_region[1]['mean']} דקות)")
        
        # תובנות נפח
        volume_data = self.analysis_results['volume_patterns']
        peak_hour = max(volume_data['peak_hours'].items(), key=lambda x: x[1])
        insights.append(f"שעת השיא: {peak_hour[0]}:00 עם {peak_hour[1]} בקשות")
        
        # תובנות סוגי תקלות
        issue_data = self.analysis_results['issue_distribution']
        insights.append(f"התקלה הנפוצה ביותר: {issue_data['most_common_issue']} ({issue_data['issue_percentages'][issue_data['most_common_issue']]}%)")
        
        # תובנות ביצועים
        status_data = self.analysis_results['status_performance']
        insights.append(f"אחוז פתרון בקשות: {status_data['resolved_rate']}%")
        
        return insights 