# Swift Ship Tracker
A complete shipment tracking and delivery management system built with Python, Flask, SQLite, HTML, CSS and JavaScript.

## Features
- Registration/login with hashed passwords
- Customer dashboard and shipment creation
- Unique tracking IDs and timeline
- Admin dashboard and status updates
- Responsive frontend
- SQLite database
- JSON tracking API
- Automated tests

## Run locally
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python seed.py
python app.py
```
Open `http://127.0.0.1:5000`.

## Demo accounts
Admin: `admin@swiftship.local` / `Admin@123`

Customer: `customer@swiftship.local` / `Customer@123`

Demo tracking ID: `SST-DEMO001`

## Project documentation
See `docs/` for project overview, requirements, system design, database design, API documentation, testing and future enhancements.

## GitHub
After downloading, create a GitHub repository named `swift-ship-tracker`, then run:
```bash
git init
git add .
git commit -m "Initial Swift Ship Tracker project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/swift-ship-tracker.git
git push -u origin main
```
