# Lembar Jawaban Analisis Praktikum RPC

## Praktikum 1 — XML-RPC

**L1.1.** Fungsi `pangkat(a, b)` menghitung `a ** b`, sedangkan `akar(x)` menghitung akar kuadrat. Fungsi akar menolak bilangan negatif karena implementasi ini hanya menangani hasil real. Keduanya didaftarkan pada server dan dipanggil melalui proxy client.

**L1.2.** Fungsi `statistik(daftar)` menerima list angka dan mengembalikan dictionary dengan kunci `min`, `max`, dan `rata2`. XML-RPC mengubah list menjadi elemen array XML dan dictionary menjadi struct XML. Dengan demikian, struktur data Python dapat dikirim melalui format XML-RPC yang didukung.

**L1.3.** XML-RPC tidak mengirim objek `datetime.datetime` Python sembarang secara langsung sebagai objek Python. Protokol XML-RPC memiliki representasi `dateTime.iso8601`; pustaka Python menyediakan tipe `xmlrpc.client.DateTime` untuk tipe tersebut. Bilangan bulat sangat besar dapat dikirim jika berada dalam rentang integer yang didukung implementasi XML-RPC/Python; batas integer 32-bit tidak boleh diasumsikan berlaku untuk semua implementasi. Uji kode mencetak hasil aktual pada lingkungan yang digunakan. Pada contoh paket, waktu dikirim sebagai string agar kompatibel secara sederhana.

**L1.4.** Program mengukur 100 pemanggilan RPC dan 100 pemanggilan fungsi lokal dengan `time.perf_counter()`. RPC lebih lambat karena setiap pemanggilan melibatkan serialisasi XML, komunikasi HTTP melalui loopback, dan pembongkaran respons. Isi angka hasil pengukuran dari komputer sendiri ke laporan.

**L1.5.** Jika server dihentikan, client umumnya menerima `ConnectionRefusedError` atau `OSError` (tergantung kondisi koneksi dan sistem operasi). Penanganannya menggunakan `try-except`, memeriksa server, alamat, port, dan firewall, lalu memberi pesan yang jelas. Untuk operasi yang mengubah data, retry harus dirancang hati-hati agar tidak menimbulkan eksekusi ganda.

**Analisis ukuran XML.** Ukuran byte harus diambil dari pesan `methodCall` yang dicetak oleh `verbose=True`, lalu dihitung menggunakan panjang byte UTF-8. Data inti untuk `tambah(5, 3)` hanya dua nilai integer, sedangkan elemen XML seperti `methodCall`, `methodName`, `params`, `param`, `value`, dan `int` merupakan overhead protokol. Rumus:
- Persentase data = (ukuran representasi nilai parameter / ukuran total pesan) × 100%.
- Persentase overhead = 100% − persentase data.
Catat ukuran persis dari output client karena spasi, header, dan versi pustaka dapat memengaruhi hasil.

## Praktikum 2 — gRPC dan Protocol Buffers

**L2.1.** `KirimBanyakNilai` menggunakan client streaming: client mengirim beberapa `NilaiRequest` melalui iterator, server menyimpan setiap nilai, menghitung jumlahnya, lalu mengirim satu `StatusResponse` setelah aliran selesai.

**L2.2.** `Diskusi` menggunakan bidirectional streaming. Client dan server dapat mengirim rangkaian pesan dalam satu RPC. Implementasi contoh mengembalikan balasan untuk setiap pesan yang diterima; ini merupakan demonstrasi aliran dua arah sederhana, bukan sistem chat multi-client lengkap.

**L2.3.** Field `prodi = 4` ditambahkan dengan nomor field baru. Protobuf dirancang agar penambahan field opsional kompatibel ke belakang: client lama yang tidak mengenal field tersebut akan mengabaikannya, sedangkan server dapat tetap memproses field yang dikenalnya. Kedua sisi harus menjaga nomor field yang sudah digunakan dan tidak mengubah tipe field secara sembarangan.

**L2.4.** Ukuran pesan dihitung dengan `len(mhs.SerializeToString())`. Hasilnya berupa ukuran serialisasi biner Protobuf dalam byte. Bandingkan dengan XML-RPC untuk data mahasiswa yang setara; XML umumnya lebih besar karena tag dan nama elemen yang berulang, sedangkan Protobuf memakai encoding biner yang lebih ringkas. Nilai tepat bergantung pada isi pesan.

**L2.5.** `stub.GetMahasiswa.future(...)` mengembalikan objek Future sehingga pemanggilan dapat berjalan tanpa menunggu satu per satu. Sepuluh Future dibuat terlebih dahulu, kemudian hasilnya diambil menggunakan `.result()`.

## Praktikum 3 — Concurrency, Timeout, dan Toleransi Kegagalan

**L3.1.** Dua puluh transfer masing-masing 10 dari A ke B menghasilkan total saldo tetap 1500. Jika semua transaksi berhasil tepat satu kali, saldo A menjadi 800 dan B menjadi 700.

**L3.2.** Jika UUID dibuat ulang pada setiap retry, server menganggap setiap percobaan sebagai permintaan baru. Ketika transfer pertama sudah diproses tetapi balasannya terlambat melewati timeout, retry dapat memproses transfer yang sama lagi. Akibatnya saldo dapat berubah lebih dari satu kali. ID yang sama harus dipakai pada seluruh percobaan untuk memungkinkan deduplikasi.

**L3.3.** `LOCK` melindungi pemeriksaan saldo, pengurangan saldo, penambahan saldo, dan pencatatan request ID sebagai satu bagian kritis. Tanpa lock, beberapa thread dapat membaca saldo yang sama sebelum perubahan thread lain tersimpan sehingga terjadi race condition. Dampaknya dapat berupa saldo tidak konsisten atau transaksi yang saling menimpa. Uji dengan menghapus lock hanya pada salinan eksperimen, bukan pada implementasi utama.

**L3.4.** Jalankan benchmark dengan `MAX_WORKERS` 1, 4, dan 10. Catat waktu total, throughput, dan latensi rata-rata dari output aktual. Secara umum, jumlah worker yang lebih besar dapat meningkatkan kemampuan menangani permintaan bersamaan sampai batas tertentu, tetapi tidak selalu mempercepat karena ada overhead thread, CPU, dan jaringan. Server contoh perlu diberi `time.sleep(0.1)` pada `GetSaldo` untuk mengikuti kondisi soal secara persis; tambahkan jeda tersebut sebelum benchmark jika diminta dosen.

| max_workers | Waktu total (s) | Throughput (req/s) | Latensi rata-rata (ms) |
|---:|---:|---:|---:|
| 1 | Isi hasil pengukuran | Isi hasil pengukuran | Isi hasil pengukuran |
| 4 | Isi hasil pengukuran | Isi hasil pengukuran | Isi hasil pengukuran |
| 10 | Isi hasil pengukuran | Isi hasil pengukuran | Isi hasil pengukuran |

**L3.5.** Failover dilakukan dengan mencoba server utama terlebih dahulu. Jika status yang diterima `UNAVAILABLE`, client mengalihkan pemanggilan ke server kedua. Untuk transfer, kedua server harus berbagi penyimpanan saldo dan deduplikasi yang konsisten; jika tidak, perpindahan server dapat menimbulkan data berbeda atau transfer ganda. Pengayaan ini membutuhkan konfigurasi dua server dan penyimpanan bersama, sehingga tidak diaktifkan pada skrip dasar.

**Pertanyaan analisis Praktikum 3.** Jika server restart, dictionary `PROSES` hilang karena hanya disimpan di memori. Server tidak lagi mengenali request ID yang pernah diproses, sehingga retry lama berpotensi mengeksekusi transaksi kembali. Perbaikannya adalah menyimpan request ID dan hasil transaksi secara persisten di database, serta melakukan pencatatan request dan perubahan saldo dalam satu transaksi database.
