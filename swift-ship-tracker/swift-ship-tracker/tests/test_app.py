import os,tempfile,pytest
os.environ['SECRET_KEY']='test-secret'
from app import app
from database import init_db
@pytest.fixture
def client():
 fd,path=tempfile.mkstemp(); os.close(fd); app.config.update(TESTING=True,DATABASE_PATH=path)
 with app.test_client() as c:
  with app.app_context(): init_db()
  yield c
 os.unlink(path)
def test_home(client): assert client.get('/').status_code==200
def test_register(client):
 r=client.post('/register',data={'name':'Test User','email':'test@example.com','password':'secret123'},follow_redirects=True); assert r.status_code==200 and b'Test User' in r.data
def test_bad_tracking(client): assert client.get('/api/track/UNKNOWN').status_code==404
