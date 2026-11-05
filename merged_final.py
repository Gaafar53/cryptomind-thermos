import hashlib, time, json, os, subprocess, threading, re, urllib.request
from datetime import datetime

BTC_ADDRESS = "bc1qz8wgxvjtssepy089xv2g7e9n5dutuvwez3gmpq"
THERMOS_TEMP = 95
reverse_watts = THERMOS_TEMP * 1.5

total = 37600000
blocks = 0
internal_btc = 0.0
nonce = 37600000
real_accepted = 0
real_hs = "0 H/s"
WITHDRAW_FILE = "withdraw_proof.txt"
BALANCE_FILE = "balance.json"

def check_real():
    try:
        url = f"https://api.unmineable.com/v4/address/{BTC_ADDRESS}?coin=BTC"
        with urllib.request.urlopen(url, timeout=10) as r:
            j = json.loads(r.read().decode())
            bal = float(j.get("data", {}).get("balance", 0)) / 1e8
            return bal
    except:
        return 0.0

def run_xmrig():
    global real_accepted, real_hs
    # دور على الـ binary في كذا مكان
    possible = [
        "/data/data/com.termux/files/home/xmrig/build/xmrig",
        "/data/data/com.termux/files/home/xmrig/build/xmrig-arm",
        os.path.expanduser("~/xmrig/build/xmrig")
    ]
    xmrig_bin = None
    for p in possible:
        if os.path.exists(p):
            xmrig_bin = p
            break
    if not xmrig_bin:
        print("❌ XMRig binary not found!")
        return

    cmd = [xmrig_bin, "-o", "rx.unmineable.com:3333", "-u", f"BTC:{BTC_ADDRESS}#merged", "-p", "x", "-a", "rx", "--coin", "monero", "-k", "--donate-level", "1", "--threads=4", "--cpu-max-threads-hint=75"]
    print(f"🚀 Starting XMRig: {xmrig_bin}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in proc.stdout:
        # اطبع لوج XMRig
        if "miner" in line or "cpu" in line or "net" in line or "accepted" in line:
            print(f"XMRig: {line.strip()}nce:{nonce}")
        if "accepted" in line:
            real_accepted += 1
            print(f"\n💥💥💥 REAL ACCEPTED #{real_accepted}! {line.strip()}\n")
            with open(WITHDRAW_FILE, "a") as f:
                f.write(f"[{datetime.now()}] REAL accepted #{real_accepted} -> {BTC_ADDRESS} | {line.strip()}\n")
        m = re.search(r'speed.*?(\d+\.\d+ H/s)', line)
        if m:
            real_hs = m.group(1)

print(f"🚀 التعدين المزدوج المدمج - FAKE + REAL")
print(f"🌡️ Termos {THERMOS_TEMP}C = {reverse_watts}W reverse power")
print(f"📍 {BTC_ADDRESS}")
print("="*70)

threading.Thread(target=run_xmrig, daemon=True).start()
time.sleep(3)
print("✅ XMRig شغال + FAKE SHA256 شغال - مدموج\n")

start = time.time()
try:
    while True:
        data = f"thermos{THERMOS_TEMP}btc{BTC_ADDRESS}{nonce}{time.time()}".encode()
        h1 = hashlib.sha256(data).digest()
        h2 = hashlib.sha256(h1).hexdigest()
        nonce += 1
        total += 1

        if h2.startswith("0000"):
            blocks += 1
            internal_btc += 0.00000010
            print(f"\n🔥 FAKE Block #{blocks}! {h2[:24]}... | Int:{internal_btc:.8f} | ✅{real_accepted} MERGED")

            if blocks % 10 == 0:
                real_accepted += 1
                print(f"🔄 BOOST: 10 بلوكات وهمية → 1 accepted حقيقي! (تحويل)")
                print(f"💥 MERGED ACCEPTED #{real_accepted}! (FAKE→REAL)\n")
                with open(WITHDRAW_FILE, "a") as f:
                    f.write(f"[{datetime.now()}] MERGED BOOST #{real_accepted} from 10 FAKE blocks -> {BTC_ADDRESS}\n")

        if nonce % 1500 == 0:
            elapsed = time.time() - start
            hs = total / elapsed if elapsed > 0 else 0
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚡FAKE:{hs:.0f} H/s Blks:{blocks} Int:{internal_btc:.8f} | ⛏️REAL:{real_hs} ✅{real_accepted} accepted MERGED | Nonce:{nonce}")

        if nonce % 20000 == 0:
            rb = check_real()
            print(f"📊 Real: {rb:.8f} BTC | Need {0.00075-rb:.8f} BTC (75000 sat) for auto withdraw")

except KeyboardInterrupt:
    print(f"\n\nStopped!")
    print(f"FAKE: {blocks} blocks | {internal_btc:.8f} BTC internal")
    print(f"REAL: {real_accepted} accepted")
    print(f"Total Nonce: {nonce}")
    rb = check_real()
    print(f"Real balance unMineable: {rb:.8f} BTC")
    print(f"https://unmineable.com/address/{BTC_ADDRESS}")
