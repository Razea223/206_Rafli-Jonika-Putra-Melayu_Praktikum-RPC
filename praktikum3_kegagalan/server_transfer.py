import random
import threading
import time
from concurrent import futures
import grpc
import rpc_transfer_pb2 as pb
import rpc_transfer_pb2_grpc as pb_grpc

MAX_WORKERS = 10  # ubah menjadi 1, 4, dan 10 untuk pengujian throughput
SALDO = {"A": 1000.0, "B": 500.0}
PROSES = {}  # request_id -> hasil; disimpan di memori
LOCK = threading.Lock()

class TransferService(pb_grpc.TransferServiceServicer):
    def Transfer(self, request, context):
        with LOCK:
            if request.request_id in PROSES:
                return PROSES[request.request_id]

            if request.dari not in SALDO or request.ke not in SALDO:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Akun tidak dikenal")
            if request.jumlah <= 0:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Jumlah harus positif")

            if SALDO[request.dari] < request.jumlah:
                hasil = pb.StatusResponse(sukses=False, pesan="Saldo tidak cukup")
            else:
                SALDO[request.dari] -= request.jumlah
                SALDO[request.ke] += request.jumlah
                hasil = pb.StatusResponse(sukses=True, pesan=f"Transfer berhasil; saldo={SALDO.copy()}")
            PROSES[request.request_id] = hasil

        # Simulasi respons lambat setelah transaksi tercatat.
        if random.random() < 0.3:
            time.sleep(3)
        return hasil

    def GetSaldo(self, request, context):
        time.sleep(0.1)  # simulasi beban untuk pengukuran throughput L3.4
        with LOCK:
            return pb.SaldoResponse(saldo_a=SALDO["A"], saldo_b=SALDO["B"])

    def ResetSaldo(self, request, context):
        with LOCK:
            SALDO.update({"A": 1000.0, "B": 500.0})
            PROSES.clear()
        return pb.StatusResponse(sukses=True, pesan="Saldo dan cache request direset")

import sys

def serve(port=50052):
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
    )

    pb_grpc.add_TransferServiceServicer_to_server(
        TransferService(), server
    )

    server.add_insecure_port(f"[::]:{port}")
    server.start()

    print(
        f"Server transfer berjalan di port {port} "
        f"(max_workers={MAX_WORKERS})..."
    )

    server.wait_for_termination()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50052
    serve(port)