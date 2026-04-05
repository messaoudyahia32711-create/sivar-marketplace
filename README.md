# Sivar Marketplace Platform 🏆

Sivar is a premium, multi-tenant marketplace platform built for e-commerce, institutional commerce, and business incubation. It features a robust Python/Django backend handling multiple authenticated environments and four distinct React dashboards providing seamless user experiences.

## 🌟 Ecosystem Overview

The platform operates on a central Django API which serves four interconnected React frontends (Dashboards):
1. **Django Backend (Port 8000)**: Handling authentication, databases (SQLite/MySQL), logic, and APIs.
2. **Vendor Dashboard (Port 5174)**: Real-time inventory and store management for sellers.
3. **Customer Dashboard (Port 5175)**: The storefront interface for standard consumers.
4. **Institution Dashboard (Port 5176)**: Purchasing and supply management for clinics and hospitals.
5. **Incubator Dashboard (Port 5177)**: Statistical tracking and management for business incubators and startups.

---

## 🛠 Tech Stack
- **Backend**: Django 5.1.4, Django REST Framework, Simple JWT Auth, SQLite.
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, TanStack Query.
- **Styling**: Highly customized dark/gold UI reflecting a premium aesthetic.

---

## 🚀 Quick Start Guide

To run the full suite locally, follow these steps:

### 1. Start the Backend
Open a terminal in the root directory:
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # (Windows)
# source venv/bin/activate # (Mac/Linux)

# Install dependencies
pip install -r requirements.txt

# Run the Django server
python manage.py runserver 0.0.0.0:8000
```

### 2. Start the Dashboards
You will need multiple terminals (or a script like `start_vites.ps1` previously used) to run the frontends:
```bash
cd vendor-dashboard
npm install
npm run dev
# Repeat the same for customer-dashboard, institution-dashboard, and incubator-dashboard.
```

---

## 🔑 Test Credentials 

A generic testing password `123456789` has been configured for all accounts. Use the following usernames based on the dashboard you are testing:

### Vendor Dashboard
- `store_alaa_cosmetique`
- `store_tibb_soukahras`
- `store_nur_derm`

### Institution Dashboard
- `atlas_wellbeing`
- `rouhi_clinic`

### Incubator Dashboard
- `incubator_soukahras`
- `incubator_alger3`

### Customer Dashboard
- `admin_sivar`

*(Please refer to the actual database or `github_plan.md` for a complete list of users).*

---

## 🔒 Security Practices
- Environment variables and keys must be handled safely.
- The `.gitignore` has been properly configured to avoid leaking `db.sqlite3`, `.env`, and uncompiled directories like `node_modules` and `venv`.