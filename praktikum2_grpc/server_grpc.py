import time
from concurrent import futures
import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

DATA = {
    "2023001": {"nama": "Andi", "prodi": "Informatika",
                "nilai": {"Basis Data": 85.0, "Jaringan": 78.0}},
    "2023002": {"nama": "Sari", "prodi": "Sistem Informasi",
                "nilai": {"Basis Data": 92.0}},
}

class LayananNilai(pb_grpc.LayananNilaiServicer):
    def GetMahasiswa(self, request, context):
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"NIM {request.nim} tidak ditemukan")
        daftar = list(mhs["nilai"].values())
        ipk = sum(daftar) / len(daftar) / 25 if daftar else 0.0
        return pb.Mahasiswa(
            nim=request.nim, nama=mhs["nama"], ipk=round(ipk, 2),
            prodi=mhs.get("prodi", "")
        )

    def TambahNilai(self, request, context):
        if not 0 <= request.nilai <= 100:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Nilai harus 0–100")
        mhs = DATA.setdefault(request.nim, {"nama": "(baru)", "prodi": "", "nilai": {}})
        mhs["nilai"][request.matkul] = request.nilai
        return pb.StatusResponse(sukses=True, pesan="Nilai tersimpan")

    def StreamNilai(self, request, context):
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "NIM tidak ditemukan")
        for matkul, nilai in mhs["nilai"].items():
            yield pb.Nilai(matkul=matkul, nilai=nilai)
            time.sleep(0.5)

    def KirimBanyakNilai(self, request_iterator, context):
        jumlah = 0
        for request in request_iterator:
            if not 0 <= request.nilai <= 100:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Nilai harus 0–100")
            mhs = DATA.setdefault(request.nim, {"nama": "(baru)", "prodi": "", "nilai": {}})
            mhs["nilai"][request.matkul] = request.nilai
            jumlah += 1
        return pb.StatusResponse(sukses=True, pesan=f"{jumlah} nilai tersimpan")

    def Diskusi(self, request_iterator, context):
        # Demo sederhana: setiap pesan yang diterima dikirim kembali sebagai balasan server.
        for pesan in request_iterator:
            yield pb.Pesan(pengirim="Server", isi=f"Pesan diterima dari {pesan.pengirim}: {pesan.isi}")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_LayananNilaiServicer_to_server(LayananNilai(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server gRPC berjalan di port 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
