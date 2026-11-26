"""Probe: drives headless Edge over CDP (no driver needed) and times Page.captureScreenshot. Stage 4 starting point."""
import subprocess, time, json, base64, requests, websocket
E=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
url="file:///C:/Users/tikel/claude/.claude/worktrees/hanukkiah-jacob-agam-fountain-27fe85/agam-hanukkiah/video/storyboard/frames/scene04.svg"
p=subprocess.Popen([E,"--headless","--disable-gpu","--remote-debugging-port=9333","--allow-file-access-from-files","--hide-scrollbars","--window-size=1920,1080","--user-data-dir=C:/Users/tikel/AppData/Local/Temp/edgecdp",url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for _ in range(40):
    try:
        tabs=requests.get("http://127.0.0.1:9333/json").json(); 
        pg=[t for t in tabs if t["type"]=="page"][0]; break
    except Exception: time.sleep(0.5)
ws=websocket.create_connection(pg["webSocketDebuggerUrl"],max_size=None)
n=[0]
def call(m,**pa):
    n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":pa}))
    while True:
        r=json.loads(ws.recv())
        if r.get("id")==n[0]: return r
time.sleep(2)
call("Emulation.setDeviceMetricsOverride",width=1920,height=1080,deviceScaleFactor=1,mobile=False)
for fmt,kw in (("jpeg",{"quality":92}),("png",{})):
    t=time.time()
    for i in range(20):
        r=call("Page.captureScreenshot",format=fmt,**kw)
    print(fmt,"20 frames",round(time.time()-t,2),"s", len(base64.b64decode(r["result"]["data"])),"bytes")
p.terminate()
