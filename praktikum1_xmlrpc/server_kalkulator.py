from datetime import datetime
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import DateTime

def tambah(a, b):
    return a + b

def kali(a, b):
    return a * b

def bagi(a, b):
    if b == 0:
        raise ValueError("Pembagian dengan nol")
    return a / b

def pangkat(a, b):
    return a ** b

def akar(x):
    if x < 0:
        raise ValueError("Akar bilangan negatif tidak didukung")
    return x ** 0.5

def statistik(daftar):
    if not daftar:
        raise ValueError("Daftar angka tidak boleh kosong")
    return {
        "min": min(daftar),
        "max": max(daftar),
        "rata2": sum(daftar) / len(daftar)
    }

def waktu_sekarang():
    # XML-RPC memiliki tipe khusus DateTime; dikirim sebagai objek datetime XML-RPC.
    return DateTime(datetime.now())

server = SimpleXMLRPCServer(
    ("0.0.0.0", 8000),
    allow_none=True,
    logRequests=True
)
server.register_introspection_functions()
for fungsi in (tambah, kali, bagi, pangkat, akar, statistik, waktu_sekarang):
    server.register_function(fungsi)

print("Server XML-RPC berjalan di port 8000...")
server.serve_forever()
