import time
import uuid
from concurrent.futures import ThreadPoolExecutor
import grpc
import rpc_transfer_pb2 as pb
import rpc_transfer_pb2_grpc as pb_grpc

def transfer_dengan_retry(stub, dari, ke, jumlah, maks=3, uuid_baru_setiap_retry=False):
    rid = str(uuid.uuid4())
    for percobaan in range(1, maks + 1):
        if uuid_baru_setiap_retry:
            rid = str(uuid.uuid4())  # sengaja salah untuk eksperimen L3.2
        req = pb.TransferRequest(request_id=rid, dari=dari, ke=ke, jumlah=jumlah)
        try:
            return stub.Transfer(req, timeout=2.0)
        except grpc.RpcError as e:
            bisa_ulang = e.code() in (
                grpc.StatusCode.DEADLINE_EXCEEDED,
                grpc.StatusCode.UNAVAILABLE
            )
            if not bisa_ulang or percobaan == maks:
                raise
            jeda = 0.5 * (2 ** (percobaan - 1))
            print(f"Percobaan {percobaan} gagal ({e.code().name}), ulang dalam {jeda}s")
            time.sleep(jeda)

def saldo(stub):
    s = stub.GetSaldo(pb.Empty())
    print(f"Saldo A={s.saldo_a:.2f}, B={s.saldo_b:.2f}, total={s.saldo_a+s.saldo_b:.2f}")

with grpc.insecure_channel("localhost:50052") as channel:
    stub = pb_grpc.TransferServiceStub(channel)
    stub.ResetSaldo(pb.Empty())
    print("Saldo awal:"); saldo(stub)

    # L3.1: 20 transfer x 10 dengan request ID unik per transaksi.
    print("\\nL3.1 - 20 transfer masing-masing 10")
    for _ in range(20):
        try:
            transfer_dengan_retry(stub, "A", "B", 10)
        except grpc.RpcError as e:
            print("Transfer gagal:", e.code())
    saldo(stub)
    print("Ekspektasi: total 1500 dan saldo A=800, B=700.")

    # L3.2: demonstrasi pola ID baru pada setiap retry.
    # Untuk melihat duplikasi, ulangi beberapa kali; sleep acak server dapat memicu timeout.
    print("\\nL3.2 - Demonstrasi retry dengan UUID baru setiap percobaan")
    stub.ResetSaldo(pb.Empty())
    try:
        transfer_dengan_retry(stub, "A", "B", 10, uuid_baru_setiap_retry=True)
    except grpc.RpcError as e:
        print("Percobaan berakhir:", e.code())
    saldo(stub)

    # L3.3: 50 permintaan serentak dari 10 thread client.
    print("\\nL3.3 - 50 transfer concurrent dari 10 thread")
    stub.ResetSaldo(pb.Empty())
    def satu_transfer(i):
        local_stub = pb_grpc.TransferServiceStub(channel)
        req = pb.TransferRequest(request_id=f"concurrent-{i}", dari="A", ke="B", jumlah=1)
        try:
            return local_stub.Transfer(req, timeout=5)
        except grpc.RpcError as e:
            return f"Gagal: {e.code().name}"
    with ThreadPoolExecutor(max_workers=10) as pool:
        hasil = list(pool.map(satu_transfer, range(50)))
    print("Jumlah hasil:", len(hasil))
    saldo(stub)
