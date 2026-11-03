import time
from concurrent.futures import ThreadPoolExecutor
import grpc
import rpc_transfer_pb2 as pb
import rpc_transfer_pb2_grpc as pb_grpc

TOTAL_REQUEST = 200
JUMLAH_THREAD = 20

def jalankan_benchmark(stub):
    def panggil(i):
        mulai = time.perf_counter()
        try:
            stub.GetSaldo(pb.Empty(), timeout=10)
        except grpc.RpcError:
            pass
        return time.perf_counter() - mulai

    mulai_total = time.perf_counter()
    with ThreadPoolExecutor(max_workers=JUMLAH_THREAD) as pool:
        latensi = list(pool.map(panggil, range(TOTAL_REQUEST)))
    total = time.perf_counter() - mulai_total
    throughput = TOTAL_REQUEST / total if total else 0
    rata2_ms = (sum(latensi) / len(latensi)) * 1000 if latensi else 0
    return total, throughput, rata2_ms

if __name__ == "__main__":
    print("Pastikan server aktif. Ubah MAX_WORKERS di server_transfer.py menjadi 1, 4, lalu 10.")
    with grpc.insecure_channel("localhost:50052") as channel:
        stub = pb_grpc.TransferServiceStub(channel)
        total, throughput, latensi = jalankan_benchmark(stub)
        print("\\nHasil satu konfigurasi:")
        print(f"Jumlah permintaan       : {TOTAL_REQUEST}")
        print(f"Jumlah thread client    : {JUMLAH_THREAD}")
        print(f"Waktu total             : {total:.4f} detik")
        print(f"Throughput              : {throughput:.2f} req/s")
        print(f"Latensi rata-rata       : {latensi:.2f} ms")
