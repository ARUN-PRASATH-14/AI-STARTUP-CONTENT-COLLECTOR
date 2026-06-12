
# 📊 Automated Data Collection System

> A fully automated data pipeline that collects real-time information from public web sources and APIs, processes it, and stores it in a structured cloud database using Supabase — with complete CI/CD automation via GitHub Actions.

---

## 🚀 Live Demo

* 🌐 Streamlit App: [https://automated-data-collection.streamlit.app/](https://automated-data-collection.streamlit.app/)
* 📦 GitHub Repo: [https://github.com/ARUN-PRASATH-14/-Automated-Data-Collection-System-](https://github.com/ARUN-PRASATH-14/-Automated-Data-Collection-System-)
* 🗄️ Database: Supabase (PostgreSQL Cloud)

---

## 📌 Project Overview

This project is an **end-to-end automated data collection system** built for internship screening purposes. It demonstrates how modern data pipelines work using:

* Web scraping from news/blog websites
* API-based data collection (Hacker News API)
* Cloud database storage (Supabase)
* Full automation using GitHub Actions
* Dashboard visualization using Streamlit

The system runs automatically with minimal or no manual intervention.

---

## 🎯 Key Features

* 🔄 Fully automated data pipeline
* 🌍 Multi-source data collection (Scraping + API)
* 🗄️ Cloud-based storage using Supabase
* ⚙️ CI/CD automation with GitHub Actions
* 📊 Real-time dashboard using Streamlit
* 🔐 Secure credential management using environment variables
* 📈 Scalable and modular architecture

---

## 🏗️ System Architecture

```
                ┌──────────────────────────┐
                │   Data Sources           │
                │  - TechCrunch            │
                │  - Anthropic Blog        │
                │  - Hacker News API       │
                └──────────┬──────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │ Data Collection Layer    │
                │ - Web Scraping           │
                │ - API Requests           │
                └──────────┬──────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │ Data Processing Layer    │
                │ - Cleaning               │
                │ - Normalization         │
                └──────────┬──────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │ Storage Layer            │
                │ Supabase (PostgreSQL)    │
                └──────────┬──────────────┘
                           │
                           ▼
        ┌────────────────────────────────────┐
        │ Visualization Layer (Streamlit)    │
        └────────────────────────────────────┘

Automation: GitHub Actions (Scheduled Runs)
```

---

## ⚙️ Tech Stack

| Layer           | Technology              |
| --------------- | ----------------------- |
| Language        | Python 3                |
| Web Scraping    | BeautifulSoup, Requests |
| API Integration | REST API (Hacker News)  |
| Database        | Supabase (PostgreSQL)   |
| Automation      | GitHub Actions (CI/CD)  |
| Dashboard       | Streamlit               |
| Deployment      | Streamlit Cloud         |

---

## 📡 Data Sources

### 1. TechCrunch

* Type: Blog / News Website
* Method: Web Scraping
* Data: Articles, titles, links

### 2. Anthropic Blog

* Type: Official company blog
* Method: Web Scraping
* Data: Product updates, posts

### 3. Hacker News

* Type: Public API
* Method: REST API
* Data: Stories, metadata (JSON format)

---

## 🔄 Data Pipeline Workflow

1. Data is collected from multiple sources
2. Scraper/API extracts relevant fields
3. Data is cleaned and structured into JSON format
4. Data is stored in Supabase database
5. Streamlit dashboard fetches and displays results
6. GitHub Actions triggers automation on schedule

---

## 🗄️ Database Schema (Supabase)

| Column    | Type     | Description       |
| --------- | -------- | ----------------- |
| title     | text     | Article title     |
| source    | text     | Source platform   |
| url       | text     | Article link      |
| timestamp | datetime | Time of insertion |

---

## 🤖 Automation (GitHub Actions)

The system is fully automated using GitHub Actions:

* ⏰ Scheduled execution (cron jobs)
* 🔁 Manual trigger support
* ☁️ Cloud-based execution
* 📦 No local machine dependency

Example workflow:

```yaml
on:
  schedule:
    - cron: "0 * * * *"
  workflow_dispatch:
```

---

## 🧠 Key Concepts Used

### 🔹 Web Scraping

Extracting data from HTML pages using BeautifulSoup by parsing DOM elements.

### 🔹 API Integration

Fetching structured JSON data directly from public APIs (Hacker News).

### 🔹 Automation (CI/CD)

GitHub Actions runs the Python pipeline automatically at scheduled intervals.

### 🔹 Cloud Database (Supabase)

PostgreSQL-based cloud database used for structured and scalable storage.

### 🔹 Cookies & Sessions (Conceptual)

Used in web systems for authentication and tracking (not required for selected public sources).

---

## ⚠️ Challenges Faced

* Handling dynamic website structures
* Differences between API and HTML data formats
* Managing environment variables in deployment
* Ensuring consistent automation via GitHub Actions
* Supabase connection issues in cloud deployment

---

## 🛠️ Solutions Implemented

* Hybrid approach (Scraping + API)
* Standardized JSON data structure
* Secure secret management using environment variables
* GitHub Actions for reliable automation
* Streamlit Cloud deployment for dashboard access

---

## 🚀 Future Improvements

* Add more data sources (Reddit, Twitter APIs)
* Implement sentiment analysis on collected data
* Add filtering and search in dashboard
* Build real-time streaming pipeline
* Add email/notification alerts for new data
* Improve analytics dashboard with charts

---

## 📁 Project Structure

```
project/
│
├── main.py
├── scrapers/
├── api/
├── supabase_client.py
├── app.py
├── requirements.txt
│
├── .github/
│   └── workflows/
│       └── automation.yml
│
└── README.md
```

---

## 👨‍💻 Author

**Arun Prasath**
Internship Project – Automated Data Collection System

---

## 🏁 Conclusion

This project demonstrates a complete **real-world data engineering pipeline** including:

✔ Data collection
✔ Data processing
✔ Cloud storage
✔ Automation
✔ Visualization

It simulates how modern production-level data pipelines operate in industry environments.

---

