import os
os.environ["DATABASE_URL"]="sqlite:///./test_codeguard.db"
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base,engine
Base.metadata.drop_all(engine);Base.metadata.create_all(engine)
client=TestClient(app)
def test_health(): assert client.get('/health').json()['status']=='ok'
def test_review_stats_delete():
 r=client.post('/api/reviews',json={'language':'Python','filename':'demo.py','code':'def f(items=[]):\n except:\n  pass'}); assert r.status_code==200 and r.json()['total_issues']>=2
 assert client.get('/api/stats').json()['total_reviews']>=1
 assert client.delete('/api/reviews/'+r.json()['review_id']).status_code==200
def test_invalid():
 assert client.post('/api/reviews',json={'language':'Ruby','code':'x'}).status_code==422
 assert client.post('/api/reviews',json={'language':'Python','code':''}).status_code==422
