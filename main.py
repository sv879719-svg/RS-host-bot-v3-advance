import os
import sqlite3
import uuid
import subprocess
import sys
import re
import threading
import time
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, session

# --- CONFIGURATION ---
ACCESS_KEY = "sarkar" 
SECRET_KEY = "rs_ultra_ghost_v12_final_fix"
APP_NAME = "RS Cold Hosting Private Server"

# --- VIRTUAL PATHS (Invisble to Main Folder) ---
BASE_DIR = "/tmp"
VAULT_DIR = os.path.join(BASE_DIR, ".rs_hidden_vault")
LOG_DIR = os.path.join(BASE_DIR, ".rs_ghost_logs")
DB_PATH = os.path.join(BASE_DIR, ".rs_metadata.db")

for d in [VAULT_DIR, LOG_DIR]:
    os.makedirs(d, exist_ok=True)

app = Flask(__name__)
app.secret_key = SECRET_KEY
running_engines = {}

# --- DEPENDENCY AUTO-INSTALLER ---
def check_libs(code, log_file):
    libs = re.findall(r"^(?:from|import)\s+([\w\d]+)", code, re.MULTILINE)
    standard = ['os','sys','time','re','json','sqlite3','subprocess','threading','requests','datetime','random','string','math','flask','uuid']
    with open(log_file, "a") as f:
        f.write("[System] Docker Environment: Python + PHP Connected.\n")
        for lib in set(libs):
            if lib.lower() not in standard:
                f.write(f"System: Virtualizing library -> {lib}...\n")
                f.flush()
                subprocess.run([sys.executable, "-m", "pip", "install", lib, "--no-cache-dir"], stdout=f, stderr=f)

# --- ENGINE RUNNER (THE FIX) ---
def run_ghost_engine(bid, script_path, log_path):
    try:
        # Step 1: Library Check
        with open(script_path, 'r') as f:
            code = f.read()
        check_libs(code, log_path)
        
        # THE FIX: PHP ko batana padega ki use /tmp folder se files uthani hain
        # Kyun ki aapka bot.py sari files (index.html, etc.) /tmp mein create kar raha hai.
        with open(log_path, "a") as f_log:
            f_log.write(f"\n[⚡] ENGINE BOOTED: {bid}\n")
            f_log.write(f"[🛡️] STATUS: RS SHIELD ACTIVE\n\n")
            f_log.flush()

            # Hum bot ko seedha /tmp directory ke andar execute karenge
            proc = subprocess.Popen([sys.executable, "-u", script_path], 
                                  stdout=f_log, stderr=f_log, 
                                  text=True, bufsize=1, cwd=BASE_DIR)
            running_engines[bid] = proc
            proc.wait()
    except Exception as e:
        with open(log_path, "a") as f:
            f.write(f"\n[!] VIRTUALIZATION ERROR: {str(e)}")

# --- PREMIUM INTERFACE ---
UI_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ name }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
        body { background: #010206; color: #e2e8f0; font-family: 'Space Grotesk', sans-serif; }
        .glass-card { background: #0a0c14; border: 1px solid #1e293b; border-radius: 24px; }
        .terminal-box { background: #000; color: #38bdf8; font-family: 'Consolas', monospace; height: 450px; overflow-y: auto; border: 1px solid #111; }
        .lock-btn-active { background: #2563eb !important; color: white !important; }
    </style>
</head>
<body class="p-4 lg:p-12">
    <div class="max-w-7xl mx-auto">
        {% if not authed %}
        <div class="flex flex-col items-center justify-center min-h-[85vh]">
            <div class="glass-card p-12 w-full max-w-md text-center border-t-2 border-blue-600">
                <h1 class="text-2xl font-bold uppercase italic tracking-tighter text-white">{{ name }}</h1>
                <form method="POST" action="/login" class="mt-8">
                    <input type="password" name="key" class="w-full bg-black border border-zinc-800 p-5 rounded-2xl text-center mb-6 focus:border-blue-500 outline-none text-white tracking-[0.8em]">
                    <button class="w-full bg-blue-600 p-5 rounded-2xl font-bold text-xs uppercase tracking-widest">Connect Server</button>
                </form>
            </div>
        </div>
        {% else %}
        <div class="flex flex-col lg:flex-row justify-between items-center mb-12 gap-8">
            <h1 class="text-3xl font-bold italic uppercase tracking-tighter text-white">{{ name }}</h1>
            <a href="/logout" class="bg-red-500/10 text-red-500 px-8 py-3 rounded-full text-[10px] font-bold border border-red-500/20">EXIT SYSTEM</a>
        </div>

        <div class="grid lg:grid-cols-12 gap-10">
            <div class="lg:col-span-4 space-y-8">
                <div class="glass-card p-8">
                    <h3 class="text-[11px] font-bold text-blue-400 mb-6 uppercase tracking-widest text-center italic">Virtual Deployment</h3>
                    <form id="uF" class="space-y-6">
                        <label class="block border-2 border-dashed border-zinc-800 p-10 rounded-3xl text-center cursor-pointer">
                            <input type="file" name="bot_file" id="fI" class="hidden" required>
                            <p id="fL" class="text-[10px] font-bold text-zinc-500 uppercase italic">Select Bot File (.py)</p>
                        </label>
                        <button type="submit" id="sB" class="w-full bg-blue-600 py-5 rounded-2xl font-bold text-[10px] uppercase tracking-widest">Launch Ghost Engine</button>
                    </form>
                </div>
                <div id="hList" class="space-y-3"></div>
            </div>
            <div class="lg:col-span-8">
                <div id="conBox" class="hidden glass-card p-8 border-blue-500/20 shadow-2xl">
                    <div class="flex justify-between items-center mb-6">
                        <span class="text-[10px] font-bold text-blue-400 uppercase italic">Active Log Stream: <span id="curID" class="text-white">...</span></span>
                        <button id="lBtn" onclick="toggleLock()" class="bg-zinc-900 border border-zinc-800 px-5 py-2.5 rounded-xl text-[10px] font-bold uppercase">Scroll Lock</button>
                    </div>
                    <div class="terminal-box rounded-2xl p-6" id="tw">
                        <div id="to" class="whitespace-pre-wrap leading-relaxed"></div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
    <script>
        let isLocked = false;
        function toggleLock() { isLocked = !isLocked; document.getElementById('lBtn').classList.toggle('lock-btn-active', isLocked); }
        async function loadHistory() {
            const r = await fetch('/get_history');
            const d = await r.json();
            document.getElementById('hList').innerHTML = d.list.map(b => `
                <div class="bg-black/40 border border-zinc-800/50 p-4 rounded-xl flex justify-between items-center cursor-pointer mb-2" onclick="viewLog('${b.id}')">
                    <span class="text-[10px] font-bold text-white uppercase italic truncate w-40">${b.name}</span>
                    <button onclick="event.stopPropagation(); terminate('${b.id}')" class="text-red-500"><i class="fa-solid fa-trash-can"></i></button>
                </div>
            `).join('');
        }
        if(document.getElementById('uF')) {
            document.getElementById('uF').onsubmit = async (e) => {
                e.preventDefault();
                await fetch('/deploy', { method: 'POST', body: new FormData(e.target) });
                location.reload();
            };
        }
        let p;
        function viewLog(id) {
            clearInterval(p);
            document.getElementById('conBox').classList.remove('hidden');
            document.getElementById('curID').innerText = id;
            p = setInterval(async () => {
                const r = await fetch('/fetch_logs/'+id);
                const d = await r.json();
                document.getElementById('to').innerText = d.data;
                if(!isLocked) document.getElementById('tw').scrollTop = document.getElementById('tw').scrollHeight;
            }, 2000);
        }
        async function terminate(id) { if(confirm("Terminate Ghost?")) { await fetch('/terminate/'+id); loadHistory(); } }
        loadHistory();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(UI_LAYOUT, authed=session.get('rs_auth')==True, name=APP_NAME)

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('key') == ACCESS_KEY:
        session['rs_auth'] = True
    return index()

@app.route('/logout')
def logout():
    session.clear()
    return index()

@app.route('/deploy', methods=['POST'])
def deploy():
    if not session.get('rs_auth'): return jsonify({"e":1})
    f = request.files.get('bot_file')
    bid = str(uuid.uuid4())[:8]
    # SAVE IN VIRTUAL TMP SPACE (OUTSIDE ROOT)
    path = os.path.join(VAULT_DIR, f"{bid}_{f.filename}")
    f.save(path)
    log_p = os.path.join(LOG_DIR, f"{bid}.log")
    db = sqlite3.connect(DB_PATH); db.execute("CREATE TABLE IF NOT EXISTS history (id TEXT, name TEXT, path TEXT, time TEXT)")
    db.execute("INSERT INTO history VALUES (?, ?, ?, ?)", (bid, f.filename, path, datetime.now().strftime('%H:%M:%S'))); db.commit(); db.close()
    threading.Thread(target=run_ghost_engine, args=(bid, path, log_p)).start()
    return jsonify({"s":"ok"})

@app.route('/get_history')
def get_history():
    db = sqlite3.connect(DB_PATH); db.execute("CREATE TABLE IF NOT EXISTS history (id TEXT, name TEXT, path TEXT, time TEXT)")
    c = db.cursor(); c.execute("SELECT id, name FROM history ORDER BY rowid DESC"); rows = c.fetchall(); db.close()
    return jsonify({"list": [{"id": r[0], "name": r[1]} for r in rows]})

@app.route('/fetch_logs/<bid>')
def fetch_logs(bid):
    p = os.path.join(LOG_DIR, f"{bid}.log")
    if os.path.exists(p):
        with open(p, 'r') as f: return jsonify({"data": f.read()})
    return jsonify({"data": "Ghost link established..."})

@app.route('/terminate/<bid>')
def terminate(bid):
    if bid in running_engines: running_engines[bid].kill()
    db = sqlite3.connect(DB_PATH); c = db.cursor(); c.execute("SELECT path FROM history WHERE id=?", (bid,)); res = c.fetchone()
    if res:
        try: os.remove(res[0]); os.remove(os.path.join(LOG_DIR, f"{bid}.log"))
        except: pass
        db.execute("DELETE FROM history WHERE id=?", (bid,)); db.commit()
    db.close()
    return jsonify({"s":"ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)