
import grpc
import rpc_transfer_pb2 as pb
import rpc_transfer_pb2_grpc as pb_grpc

# Daftar server utama dan server cadangan
SERVERS = [
    "localhost:50051",
    "localhost:50052",
]


def get_saldo_failover():
    """
    Menghubungi server utama terlebih dahulu.
    Jika server utama gagal, client berpindah
    ke server cadangan secara otomatis.
    """

    for address in SERVERS:
        print(f"\nMencoba menghubungi server {address}...")

        channel = grpc.insecure_channel(address)
        stub = pb_grpc.TransferServiceStub(channel)

        try:
            # Memanggil RPC GetSaldo
            response = stub.GetSaldo(
                pb.Empty(),
                timeout=2
            )

            print(f"\nBerhasil terhubung ke {address}!")
            print("Informasi saldo:")
            print(f"Saldo A: {response.saldo_a}")
            print(f"Saldo B: {response.saldo_b}")

            print("\nPengujian failover selesai.")
            return response

        except grpc.RpcError as e:
            status = e.code()

            print(
                f"Server {address} gagal: "
                f"{status.name}"
            )

            # Menangani server tidak tersedia
            if status in (
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.DEADLINE_EXCEEDED
            ):
                print("Server tidak dapat diakses.")
                print("Mencoba failover ke server berikutnya...")

            else:
                print("Terjadi error selain masalah koneksi.")
                print(f"Detail: {e.details()}")
                return None

        finally:
            channel.close()

    print("\nSemua server tidak tersedia.")
    print("Failover gagal dilakukan.")

    return None


if __name__ == "__main__":
    get_saldo_failover()