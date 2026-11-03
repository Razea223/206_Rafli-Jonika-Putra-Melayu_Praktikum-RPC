import time
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy("http://localhost:8000/", verbose=True)

print("Daftar method:", proxy.system.listMethods())
print("5 + 3 =", proxy.tambah(5, 3))
print("4 x 7 =", proxy.kali(4, 7))
print("2 pangkat 5 =", proxy.pangkat(2, 5))
print("Akar 81 =", proxy.akar(81))
print("Statistik =", proxy.statistik([2, 4, 6, 8, 10]))

try:
    print("Pembagian 10 / 0 =", proxy.bagi(10, 0))
except xmlrpc.client.Fault as e:
    print("Error dari server:", e.faultString)

# L1.3: datetime Python biasa bukan tipe XML-RPC yang didukung langsung.
# Server mengirim tipe DateTime khusus yang disediakan XML-RPC.
print("Waktu server:", proxy.waktu_sekarang())

# Bilangan lebih besar dari 2^31
angka_besar = 2 ** 40
try:
    print("Bilangan besar:", proxy.tambah(angka_besar, 1))
except OverflowError:
    print("Pengujian bilangan besar:")
    print("Gagal dikirim karena melebihi batas integer XML-RPC.")

# L1.4: bandingkan 100 pemanggilan RPC dan fungsi lokal.
n = 100
mulai = time.perf_counter()
for _ in range(n):
    proxy.tambah(5, 3)
waktu_rpc = time.perf_counter() - mulai

def tambah_lokal(a, b):
    return a + b

mulai = time.perf_counter()
for _ in range(n):
    tambah_lokal(5, 3)
waktu_lokal = time.perf_counter() - mulai

print(f"Waktu {n} pemanggilan RPC   : {waktu_rpc:.6f} detik")
print(f"Waktu {n} pemanggilan lokal : {waktu_lokal:.6f} detik")
if waktu_lokal > 0:
    print(f"RPC sekitar {waktu_rpc / waktu_lokal:.1f} kali waktu fungsi lokal")
