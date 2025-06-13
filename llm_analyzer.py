import os
import json
from datetime import datetime
from typing import Dict, List
import streamlit as st
from openai import OpenAI
from data_analyzer import ServiceDataAnalyzer

class LLMServiceAnalyzer:
    """
    מחלקה לניתוח נתוני שירות באמצעות LLM ויצירת דוחות מקצועיים
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        """
        אתחול המנתח עם מפתח API ומודל
        
        Args:
            api_key (str): מפתח OpenAI API
            model (str): שם המודל לשימוש (ברירת מחדל: gpt-4)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def analyze_with_llm(self, analysis_data: Dict) -> Dict:
        """
        ניתוח הנתונים באמצעות LLM
        
        Args:
            analysis_data (Dict): נתוני הניתוח המקיף
        
        Returns:
            Dict: מילון עם הדוח והמידע על סוג הניתוח
        """
        if not self.client:
            return {
                'analysis': self._generate_fallback_analysis(analysis_data),
                'analysis_type': 'basic',
                'model_used': None,
                'api_used': False
            }
        
        # בדיקה שמפתח ה-API תקין
        if not self.api_key or len(self.api_key.strip()) < 10:
            return {
                'analysis': self._generate_fallback_analysis(analysis_data),
                'analysis_type': 'basic_invalid_key',
                'model_used': None,
                'api_used': False,
                'error': 'מפתח API לא תקין או חסר'
            }
        
        # הכנת הנתונים לשליחה ל-LLM
        data_summary = self._prepare_data_for_llm(analysis_data)
        
        prompt = f"""
        אתה מנתח נתונים מקצועי המתמחה בניתוח ביצועי שירות לחברות סיוע בדרכים.
        
        **התחל את הדוח עם הכותרת הבאה:**
        "🤖 **ניתוח מתקדם עם בינה מלאכותית - {self.model}**"
        
        נתוני השירות שלפניך:
        {data_summary}
        
        אנא צור דוח מקצועי ומפורט הכולל:
        
        1. **סיכום מנהלים** - תמצית של 2-3 משפטים עם הממצאים העיקריים
        
        2. **ממצאים עיקריים**:
           - ביצועי זמני מענה
           - דפוסי נפח בקשות
           - ניתוח סוגי תקלות
           - ביצועי פתרון בקשות
           - דפוסים גיאוגרפיים
        
        3. **בעיות מזוהות**:
           - אזורים או זמנים בעייתיים
           - תקלות מורכבות
           - חוסרי יעילות
        
        4. **הזדמנויות לשיפור**:
           - המלצות קונקרטיות
           - אופטימיזציה של משאבים
           - שיפור תהליכים
        
        5. **המלצות לפעולה**:
           - צעדים מיידיים
           - תכנון ארוך טווח
           - מדדי הצלחה
        
        הדוח צריך להיות מקצועי, ברור ומעשי עבור מנהלים.
        כתוב בעברית ובסגנון עסקי פורמלי.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "אתה מנתח נתונים מקצועי המתמחה בניתוח ביצועי שירות."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return {
                'analysis': response.choices[0].message.content,
                'analysis_type': 'llm',
                'model_used': self.model,
                'api_used': True,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            st.error(f"שגיאה בחיבור ל-OpenAI: {str(e)}")
            return {
                'analysis': self._generate_fallback_analysis(analysis_data),
                'analysis_type': 'basic_fallback',
                'model_used': None,
                'api_used': False,
                'error': str(e)
            }
    
    def _prepare_data_for_llm(self, analysis_data: Dict) -> str:
        """
        הכנת הנתונים לשליחה ל-LLM
        
        Args:
            analysis_data (Dict): נתוני הניתוח
        
        Returns:
            str: נתונים מעובדים לשליחה
        """
        summary = []
        
        # מטא-דאטה
        metadata = analysis_data['metadata']
        summary.append(f"תקופת הניתוח: {metadata['date_range']['start']} עד {metadata['date_range']['end']}")
        summary.append(f"סה\"כ בקשות: {metadata['total_records']}")
        
        # זמני מענה
        response_times = analysis_data['response_times']
        summary.append(f"זמן מענה ממוצע: {response_times['overall_avg']} דקות")
        
        if response_times['problematic_regions']:
            summary.append("אזורים בעייתיים:")
            for region, stats in response_times['problematic_regions'].items():
                summary.append(f"  - {region}: {stats['mean']} דקות ממוצע")
        
        # דפוסי נפח
        volume = analysis_data['volume_patterns']
        summary.append(f"ממוצע בקשות יומי: {volume['avg_daily_requests']}")
        summary.append(f"שעות שיא: {list(volume['peak_hours'].keys())}")
        
        # סוגי תקלות
        issues = analysis_data['issue_distribution']
        summary.append(f"התקלה הנפוצה ביותר: {issues['most_common_issue']} ({issues['issue_percentages'][issues['most_common_issue']]}%)")
        
        # ביצועי פתרון
        status = analysis_data['status_performance']
        summary.append(f"אחוז פתרון: {status['resolved_rate']}%")
        
        return "\n".join(summary)
    
    def _generate_fallback_analysis(self, analysis_data: Dict) -> str:
        """
        יצירת ניתוח בסיסי במקרה שאין חיבור ל-LLM
        
        Args:
            analysis_data (Dict): נתוני הניתוח
        
        Returns:
            str: דוח בסיסי
        """
        report = []
        
        report.append("# דוח ניתוח ביצועי שירות - ניתוח בסיסי")
        report.append(f"תאריך יצירה: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("⚠️ **הערה: זהו ניתוח בסיסי שנוצר ללא שימוש ב-API של OpenAI**")
        report.append("לקבלת ניתוח מתקדם יותר עם תובנות עמוקות, הכנס מפתח OpenAI API.")
        report.append("")
        
        # סיכום מנהלים
        report.append("## סיכום מנהלים")
        metadata = analysis_data['metadata']
        response_times = analysis_data['response_times']
        status = analysis_data['status_performance']
        
        report.append(f"נותחו {metadata['total_records']} בקשות שירות מהתקופה {metadata['date_range']['start']} עד {metadata['date_range']['end']}.")
        report.append(f"זמן המענה הממוצע עומד על {response_times['overall_avg']} דקות ואחוז הפתרון הוא {status['resolved_rate']}%.")
        report.append("")
        
        # ממצאים עיקריים
        report.append("## ממצאים עיקריים")
        
        # זמני מענה
        report.append("### זמני מענה")
        report.append(f"- זמן מענה ממוצע כללי: {response_times['overall_avg']} דקות")
        
        if response_times['problematic_regions']:
            report.append("- אזורים עם זמני מענה גבוהים:")
            for region, stats in response_times['problematic_regions'].items():
                report.append(f"  * {region}: {stats['mean']} דקות")
        
        # נפח בקשות
        volume = analysis_data['volume_patterns']
        report.append("\n### דפוסי נפח")
        report.append(f"- ממוצע בקשות יומי: {volume['avg_daily_requests']}")
        report.append("- שעות השיא:")
        for hour, count in list(volume['peak_hours'].items())[:3]:
            report.append(f"  * {hour}:00 - {count} בקשות")
        
        # סוגי תקלות
        issues = analysis_data['issue_distribution']
        report.append("\n### התפלגות תקלות")
        report.append(f"- התקלה הנפוצה ביותר: {issues['most_common_issue']} ({issues['issue_percentages'][issues['most_common_issue']]}%)")
        report.append("- התפלגות מלאה:")
        for issue, percentage in issues['issue_percentages'].items():
            report.append(f"  * {issue}: {percentage}%")
        
        # המלצות בסיסיות
        report.append("\n## המלצות לשיפור")
        
        if response_times['problematic_regions']:
            report.append("1. **שיפור זמני מענה באזורים בעייתיים:**")
            for region in response_times['problematic_regions'].keys():
                report.append(f"   - הגדלת כוח אדם באזור {region}")
        
        if status['resolved_rate'] < 90:
            report.append("2. **שיפור אחוז הפתרון:**")
            report.append("   - בדיקת תהליכי הטיפול בבקשות")
            report.append("   - הכשרת צוותי השירות")
        
        peak_hour = max(volume['peak_hours'].items(), key=lambda x: x[1])
        report.append("3. **אופטימיזציה לפי שעות השיא:**")
        report.append(f"   - הכנה מוגברת לשעה {peak_hour[0]}:00")
        report.append("   - תגבור כוח אדם בשעות העומס")
        
        return "\n".join(report)
    
    def generate_report_file(self, analysis_data: Dict, llm_result: Dict) -> str:
        """
        יצירת קובץ דוח מקצועי להורדה
        
        Args:
            analysis_data (Dict): נתוני הניתוח
            llm_result (Dict): תוצאת הניתוח עם מטא-דאטה
        
        Returns:
            str: תוכן הדוח המלא
        """
        report_lines = []
        
        # כותרת הדוח
        report_lines.append("=" * 80)
        report_lines.append("דוח ניתוח ביצועי שירות - Service Tracker")
        report_lines.append("=" * 80)
        report_lines.append(f"תאריך יצירה: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # מידע על סוג הניתוח
        if llm_result['api_used']:
            report_lines.append(f"סוג ניתוח: ניתוח מתקדם עם AI")
            report_lines.append(f"מודל AI: {llm_result['model_used']}")
            if llm_result.get('tokens_used'):
                report_lines.append(f"טוקנים שנוצלו: {llm_result['tokens_used']}")
        else:
            report_lines.append("סוג ניתוח: ניתוח בסיסי (ללא API)")
            if llm_result.get('error'):
                report_lines.append(f"סיבה: {llm_result['error']}")
        
        report_lines.append("")
        
        # ניתוח LLM
        report_lines.append(llm_result['analysis'])
        report_lines.append("")
        
        # נתונים מפורטים
        report_lines.append("=" * 80)
        report_lines.append("נספח: נתונים מפורטים")
        report_lines.append("=" * 80)
        
        # מטא-דאטה
        metadata = analysis_data['metadata']
        report_lines.append("## פרטי הניתוח")
        report_lines.append(f"תקופת הניתוח: {metadata['date_range']['start']} עד {metadata['date_range']['end']}")
        report_lines.append(f"סה\"כ רשומות: {metadata['total_records']}")
        report_lines.append("")
        
        # זמני מענה מפורטים
        response_times = analysis_data['response_times']
        report_lines.append("## זמני מענה לפי אזורים")
        for region, stats in response_times['region_stats'].items():
            report_lines.append(f"{region}:")
            report_lines.append(f"  ממוצע: {stats['mean']} דקות")
            report_lines.append(f"  חציון: {stats['median']} דקות")
            report_lines.append(f"  מספר בקשות: {stats['count']}")
        report_lines.append("")
        
        # התפלגות תקלות מפורטת
        issues = analysis_data['issue_distribution']
        report_lines.append("## התפלגות סוגי תקלות")
        for issue, count in issues['issue_counts'].items():
            percentage = issues['issue_percentages'][issue]
            report_lines.append(f"{issue}: {count} בקשות ({percentage}%)")
        report_lines.append("")
        
        # ביצועי סטטוס
        status = analysis_data['status_performance']
        report_lines.append("## התפלגות סטטוסים")
        for status_type, count in status['status_counts'].items():
            percentage = status['status_percentages'][status_type]
            report_lines.append(f"{status_type}: {count} בקשות ({percentage}%)")
        report_lines.append("")
        
        # חתימה
        report_lines.append("=" * 80)
        report_lines.append("דוח זה נוצר אוטומטיות על ידי מערכת Service Tracker")
        report_lines.append(f"© {datetime.now().year} Service Tracker Analytics")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines) 