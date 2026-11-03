import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

def data_nilai():
    yield pb.NilaiRequest(nim="2023001", matkul="Pemrograman", nilai=90)
    yield pb.NilaiRequest(nim="2023001", matkul="Sistem Operasi", nilai=87)
    yield pb.NilaiRequest(nim="2023002", matkul="Jaringan", nilai=89)

def data_pesan():
    yield pb.Pesan(pengirim="Client 1", isi="Halo server")
    yield pb.Pesan(pengirim="Client 1", isi="Ini pengujian streaming")

with grpc.insecure_channel("localhost:50051") as channel:
    stub = pb_grpc.LayananNilaiStub(channel)

    # Unary
    mhs = stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"))
    print(f"Mahasiswa: {mhs.nama}, Prodi: {mhs.prodi}, IPK: {mhs.ipk}")

    print(stub.TambahNilai(
        pb.NilaiRequest(nim="2023001", matkul="Komputasi Paralel", nilai=88)
    ).pesan)

    # Server streaming
    print("\\nDaftar nilai (server streaming):")
    for nilai in stub.StreamNilai(pb.MahasiswaRequest(nim="2023001")):
        print(f"{nilai.matkul}: {nilai.nilai}")

    # Client streaming
    hasil = stub.KirimBanyakNilai(data_nilai())
    print("\\nClient streaming:", hasil.pesan)

    # Bidirectional streaming
    print("\\nBidirectional streaming:")
    for balasan in stub.Diskusi(data_pesan()):
        print(f"{balasan.pengirim}: {balasan.isi}")

    # L2.4: ukuran pesan Protobuf
    ukuran = mhs.SerializeToString()
    print("\\nUkuran pesan Protobuf:", len(ukuran), "byte")
    print("Representasi pesan:", mhs)

    # L2.5: 10 panggilan asynchronous menggunakan Future
    print("\\n10 pemanggilan asynchronous:")
    futures = [
        stub.GetMahasiswa.future(pb.MahasiswaRequest(nim="2023001"))
        for _ in range(10)
    ]
    for i, future in enumerate(futures, start=1):
        hasil_async = future.result()
        print(f"Permintaan {i}: {hasil_async.nama}, IPK {hasil_async.ipk}")

    # Error NOT_FOUND
    try:
        stub.GetMahasiswa(pb.MahasiswaRequest(nim="9999"))
    except grpc.RpcError as e:
        print("\\nError:", e.code(), e.details())
