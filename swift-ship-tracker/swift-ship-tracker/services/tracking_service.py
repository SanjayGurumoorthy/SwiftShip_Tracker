import secrets,string
from database import get_db
STATUSES=['Pending','Picked Up','In Transit','Out for Delivery','Delivered','Cancelled']
def generate_tracking_id():
    db=get_db()
    while True:
        code='SST-'+''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(8))
        if not db.execute('SELECT 1 FROM shipments WHERE tracking_id=?',(code,)).fetchone(): return code
def add_tracking_event(shipment_id,status,location,note=''):
    db=get_db(); db.execute('INSERT INTO tracking_events (shipment_id,status,location,note) VALUES (?,?,?,?)',(shipment_id,status,location,note)); db.commit()
def update_status(shipment_id,status,location,note=''):
    if status not in STATUSES: raise ValueError('Invalid shipment status')
    db=get_db(); db.execute('UPDATE shipments SET status=? WHERE id=?',(status,shipment_id)); db.commit(); add_tracking_event(shipment_id,status,location,note)
