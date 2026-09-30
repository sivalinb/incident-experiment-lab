"""Standard-library HTTP broker and sink. A real broker process is killed/restarted."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import queue
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request


def post(port, data, timeout=1):
    request=urllib.request.Request(f"http://127.0.0.1:{port}/",json.dumps(data).encode(),{"Content-Type":"application/json"})
    with urllib.request.urlopen(request,timeout=timeout) as response:
        return response.status


def broker(policy, capacity):
    lock=threading.Lock()
    connection=sqlite3.connect("/tmp/queue.sqlite",check_same_thread=False)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, body TEXT)")
    pending=queue.Queue(maxsize=capacity)
    class Receiver(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            data=json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            try:
                if policy=="durable":
                    with lock:
                        count=connection.execute("SELECT count(*) FROM events").fetchone()[0]
                        if count>=capacity:
                            raise queue.Full
                        connection.execute("INSERT OR IGNORE INTO events VALUES (?,?)",(data["id"],json.dumps(data)))
                        connection.commit()
                else:
                    pending.put_nowait(data)
                self.send_response(202)
            except queue.Full:
                self.send_response(429)
            self.end_headers()
    def drain():
        active=None
        while True:
            if active is None:
                if policy=="durable":
                    with lock:
                        row=connection.execute("SELECT body FROM events ORDER BY id LIMIT 1").fetchone()
                    active=json.loads(row[0]) if row else None
                else:
                    try: active=pending.get_nowait()
                    except queue.Empty: pass
            if active is not None:
                try:
                    post(8002,active,timeout=0.5)
                    if policy=="durable":
                        with lock:
                            connection.execute("DELETE FROM events WHERE id=?",(active["id"],))
                            connection.commit()
                    active=None
                except OSError:
                    pass
            time.sleep(0.005)
    threading.Thread(target=drain,daemon=True).start()
    ThreadingHTTPServer(("127.0.0.1",8001),Receiver).serve_forever()


def experiment(config, policy):
    sink_available=threading.Event()
    sink_available.set()
    received=[]
    received_lock=threading.Lock()
    class Sink(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            data=json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if not sink_available.is_set():
                self.send_response(503)
            else:
                with received_lock:
                    received.append({**data,"received_at":time.monotonic()})
                self.send_response(200)
            self.end_headers()
    server=ThreadingHTTPServer(("127.0.0.1",8002),Sink)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    def start():
        p=subprocess.Popen([sys.executable,__file__,"broker",policy,str(config["queueCapacity"])],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        import socket
        for _ in range(100):
            try:
                with socket.create_connection(("127.0.0.1",8001),timeout=0.05): pass
                return p
            except OSError: time.sleep(0.01)
        p.kill(); p.wait()
        raise RuntimeError("Broker failed to become ready")
    process=start()
    accepted=[]
    rejected=[]
    timeline=[]
    started=time.monotonic()
    try:
        for i in range(config["events"]):
            if i==config["outageStart"]: sink_available.clear()
            if i==config["outageEnd"]: sink_available.set()
            if i==config["crashAt"]:
                process.kill(); process.wait()
                process=start()
            event={"id":i,"created_at":time.monotonic()}
            try:
                post(8001,event)
                accepted.append(i)
            except OSError:
                rejected.append(i)
            with received_lock:
                delivered=len({x["id"] for x in received})
            timeline.append({"tick":i,"queue_depth":len(accepted)-delivered,"delivered":delivered,"sink_available":int(sink_available.is_set())})
            time.sleep(0.02)
        sink_available.set()
        last=-1
        stable=0
        for _ in range(200):
            with received_lock: n=len(received)
            stable=stable+1 if n==last else 0
            last=n
            if stable>=20: break
            time.sleep(0.02)
        with received_lock: result=list(received)
        ids=[x["id"] for x in result]
        unique=set(ids)
        print(json.dumps({"policy":policy,"accepted":len(accepted),"rejected":len(rejected),"delivered_unique":len(unique),
                          "lost":len(set(accepted)-unique),"duplicates":len(ids)-len(unique),
                          "recovery_ratio":len(unique)/len(accepted) if accepted else 1,
                          "delivery_ids":ids,"lost_ids":sorted(set(accepted)-unique),"timeline":timeline,
                          "latency_ms_mean":sum((x["received_at"]-x["created_at"])*1000 for x in result)/len(result) if result else 0,
                          "wall_seconds":time.monotonic()-started}))
    finally:
        process.kill(); process.wait()
        server.shutdown()


if __name__=="__main__":
    if sys.argv[1]=="broker": broker(sys.argv[2],int(sys.argv[3]))
    else: experiment(json.loads(sys.argv[1]),sys.argv[2])
