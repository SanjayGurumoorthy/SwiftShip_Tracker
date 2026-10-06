from datetime import date,timedelta
from app import app
from database import get_db,init_db
from werkzeug.security import generate_password_hash
from services.tracking_service import add_tracking_event
with app.app_context():
 init_db(); db=get_db()
 if not db.execute("SELECT id FROM users WHERE email='admin@swiftship.local'").fetchone(): db.execute('INSERT INTO users (name,email,password_hash,role) VALUES (?,?,?,?)',('Swift Ship Admin','admin@swiftship.local',generate_password_hash('Admin@123'),'admin'))
 if not db.execute("SELECT id FROM users WHERE email='customer@swiftship.local'").fetchone(): db.execute('INSERT INTO users (name,email,password_hash,role) VALUES (?,?,?,?)',('Demo Customer','customer@swiftship.local',generate_password_hash('Customer@123'),'customer'))
 db.commit(); customer=db.execute("SELECT id FROM users WHERE email='customer@swiftship.local'").fetchone()
 if not db.execute("SELECT id FROM shipments WHERE tracking_id='SST-DEMO001'").fetchone():
  cur=db.execute("INSERT INTO shipments (tracking_id,user_id,sender_name,sender_phone,receiver_name,receiver_phone,pickup_address,delivery_address,package_description,weight,status,estimated_delivery) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",('SST-DEMO001',customer['id'],'Demo Customer','9876543210','Arun Kumar','9876501234','Chennai, Tamil Nadu','Bengaluru, Karnataka','Electronics accessories',1.5,'In Transit',(date.today()+timedelta(days=2)).isoformat())); db.commit(); sid=cur.lastrowid
  add_tracking_event(sid,'Pending','Chennai Hub','Shipment created'); add_tracking_event(sid,'Picked Up','Chennai Hub','Package picked up'); add_tracking_event(sid,'In Transit','Bengaluru Highway','Shipment is moving to destination')
print('Seed complete. Admin: admin@swiftship.local / Admin@123 | Customer: customer@swiftship.local / Customer@123 | Tracking: SST-DEMO001')
