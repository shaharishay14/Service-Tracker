# 📊 Service Tracker – Service Request Analysis Dashboard

**Service Tracker** is an interactive data analytics dashboard designed to help roadside assistance companies (like Shagrir) analyze, visualize, and gain insights from their service request data.

The project was built as a real-world use case to demonstrate how organizations can turn raw operational data into business intelligence that supports faster decision-making, improves customer satisfaction, and increases efficiency in the field.

---

## 🎯 Purpose

Modern service providers handle hundreds or thousands of service requests every day. However, without a centralized and intelligent dashboard, it’s difficult to:

- Monitor real-time performance.
- Detect geographic hotspots for delays or frequent issues.
- Understand what types of problems occur most often.
- Optimize staffing and dispatch based on patterns.

**Service Tracker solves this problem** by providing a clear and interactive dashboard that turns service request data into actionable insights.

---

## 🧠 Key Features

- 📍 **Filter by Region** – View stats for a specific city or area.
- ⏱️ **Average Response Time by Region** – Visualized using bar charts.
- ⚠️ **Most Common Issue Types** – Displayed as an interactive pie chart.
- 📅 **Requests Over Time** – Analyze how many calls come in per hour/day.
- 📊 **KPI Cards** – Show overall metrics like total requests, average response time, and percentage of resolved issues.
- 🔍 **Interactive UI** – Built using Streamlit for easy exploration.

---

## 🛠️ Tech Stack

| Area             | Technology           |
|------------------|----------------------|
| Frontend (UI)    | [Streamlit](https://streamlit.io/) |
| Data Handling    | [Pandas](https://pandas.pydata.org/) |
| Visualization    | [Plotly](https://plotly.com/python/) / Altair |
| Data Format      | JSON (simulating service call records) |
| Optional Backend | Flask or FastAPI (future expansion) |

---

## 📂 Example Data Structure (`service_requests.json`)

```json
[
  {
    "id": "REQ001",
    "opened_at": "2025-06-10T14:30:00",
    "responded_at": "2025-06-10T15:10:00",
    "region": "Tel Aviv",
    "issue_type": "Battery",
    "status": "Resolved"
  },
  ...
]
