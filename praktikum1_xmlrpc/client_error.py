import xmlrpc.client

try:
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")
    print(proxy.tambah(5, 3))
except (ConnectionRefusedError, OSError, xmlrpc.client.ProtocolError) as e:
    print("Koneksi ke server gagal:", repr(e))
    print("Penanganan: pastikan server aktif, alamat dan port benar, serta firewall mengizinkan koneksi.")
