from functools import wraps
import sqlite3
from datetime import date,timedelta
from flask import Flask,jsonify,redirect,render_template,request,session,url_for,flash
from werkzeug.security import check_password_hash,generate_password_hash
from config import Config
from database import close_db,get_db,init_db
from services.tracking_service import STATUSES,add_tracking_event,generate_tracking_id,update_status
app=Flask(__name__); app.config.from_object(Config); app.teardown_appcontext(close_db)
with app.app_context(): init_db()
def login_required(view):
 @wraps(view)
 def wrapped(*a,**k):
  if 'user_id' not in session: flash('Please log in to continue.','warning'); return redirect(url_for('login',next=request.path))
  return view(*a,**k)
 return wrapped
def admin_required(view):
 @wraps(view)
 def wrapped(*a,**k):
  if session.get('role')!='admin': flash('Administrator access is required.','danger'); return redirect(url_for('index'))
  return view(*a,**k)
 return wrapped
@app.route('/')
def index(): return render_template('index.html')
@app.route('/register',methods=['GET','POST'])
def register():
 if request.method=='POST':
  name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
  if not name or not email or len(password)<6: flash('Enter all details. Password must be at least 6 characters.','danger'); return render_template('register.html')
  try:
   db=get_db(); cur=db.execute('INSERT INTO users (name,email,password_hash) VALUES (?,?,?)',(name,email,generate_password_hash(password))); db.commit()
  except sqlite3.IntegrityError: flash('An account with that email already exists.','danger'); return render_template('register.html')
  session.clear(); session.update(user_id=cur.lastrowid,name=name,role='customer'); return redirect(url_for('dashboard'))
 return render_template('register.html')
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  email=request.form.get('email','').strip().lower(); password=request.form.get('password',''); user=get_db().execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
  if user and check_password_hash(user['password_hash'],password):
   session.clear(); session.update(user_id=user['id'],name=user['name'],role=user['role']); return redirect(url_for('admin' if user['role']=='admin' else 'dashboard'))
  flash('Invalid email or password.','danger')
 return render_template('login.html')
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))
@app.route('/dashboard')
@login_required
def dashboard():
 rows=get_db().execute('SELECT * FROM shipments WHERE user_id=? ORDER BY created_at DESC',(session['user_id'],)).fetchall(); counts={}
 for r in rows: counts[r['status']]=counts.get(r['status'],0)+1
 return render_template('dashboard.html',shipments=rows,counts=counts)
@app.route('/shipments/new',methods=['GET','POST'])
@login_required
def create_shipment():
 if request.method=='POST':
  names=['sender_name','sender_phone','receiver_name','receiver_phone','pickup_address','delivery_address','package_description','weight']; data={n:request.form.get(n,'').strip() for n in names}
  if not all(data.values()): flash('Please complete every field.','danger'); return render_template('create_shipment.html')
  try: weight=float(data['weight']); assert weight>0
  except: flash('Weight must be a positive number.','danger'); return render_template('create_shipment.html')
  tid=generate_tracking_id(); eta=(date.today()+timedelta(days=4)).isoformat(); db=get_db(); cur=db.execute('INSERT INTO shipments (tracking_id,user_id,sender_name,sender_phone,receiver_name,receiver_phone,pickup_address,delivery_address,package_description,weight,status,estimated_delivery) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(tid,session['user_id'],data['sender_name'],data['sender_phone'],data['receiver_name'],data['receiver_phone'],data['pickup_address'],data['delivery_address'],data['package_description'],weight,'Pending',eta)); db.commit(); add_tracking_event(cur.lastrowid,'Pending',data['pickup_address'],'Shipment created'); return redirect(url_for('track',tracking_id=tid))
 return render_template('create_shipment.html')
@app.route('/track',methods=['GET','POST'])
def track_form():
 tid=(request.form.get('tracking_id','') if request.method=='POST' else request.args.get('tracking_id','')).strip()
 return redirect(url_for('track',tracking_id=tid)) if tid else render_template('track.html',shipment=None,events=[])
@app.route('/track/<tracking_id>')
def track(tracking_id):
 db=get_db(); shipment=db.execute('SELECT * FROM shipments WHERE tracking_id=?',(tracking_id.upper(),)).fetchone(); events=db.execute('SELECT * FROM tracking_events WHERE shipment_id=? ORDER BY event_time ASC,id ASC',(shipment['id'],)).fetchall() if shipment else []; 
 if not shipment: flash('Tracking ID not found.','danger')
 return render_template('track.html',shipment=shipment,events=events)
@app.route('/api/track/<tracking_id>')
def api_track(tracking_id):
 db=get_db(); s=db.execute('SELECT * FROM shipments WHERE tracking_id=?',(tracking_id.upper(),)).fetchone()
 if not s: return jsonify(error='Shipment not found'),404
 e=db.execute('SELECT status,location,note,event_time FROM tracking_events WHERE shipment_id=? ORDER BY event_time ASC,id ASC',(s['id'],)).fetchall()
 return jsonify(tracking_id=s['tracking_id'],status=s['status'],receiver=s['receiver_name'],delivery_address=s['delivery_address'],estimated_delivery=s['estimated_delivery'],events=[dict(x) for x in e])
@app.route('/admin')
@login_required
@admin_required
def admin():
 db=get_db(); rows=db.execute('SELECT s.*,u.name customer_name,u.email customer_email FROM shipments s JOIN users u ON u.id=s.user_id ORDER BY s.created_at DESC').fetchall(); stats={'total':db.execute('SELECT COUNT(*) FROM shipments').fetchone()[0],'delivered':db.execute("SELECT COUNT(*) FROM shipments WHERE status='Delivered'").fetchone()[0],'in_transit':db.execute("SELECT COUNT(*) FROM shipments WHERE status='In Transit'").fetchone()[0],'pending':db.execute("SELECT COUNT(*) FROM shipments WHERE status='Pending'").fetchone()[0]}; return render_template('admin.html',shipments=rows,stats=stats,statuses=STATUSES)
@app.route('/admin/shipments/<int:shipment_id>/status',methods=['POST'])
@login_required
@admin_required
def admin_update_status(shipment_id):
 try: update_status(shipment_id,request.form.get('status',''),request.form.get('location','').strip() or 'Swift Ship Hub',request.form.get('note','').strip()); flash('Shipment status updated.','success')
 except ValueError: flash('Invalid status.','danger')
 return redirect(url_for('admin'))
@app.errorhandler(404)
def not_found(e): return render_template('404.html'),404
if __name__=='__main__': app.run(debug=True)
