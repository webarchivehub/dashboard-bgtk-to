BGTK SCHOOL ASSESSMENT ANALYTICS — TO 1 & TO 2

ISI PAKET
- app.py: aplikasi Streamlit gabungan dengan tampilan dan fitur dashboard yang disetujui, ditambah unggah TO 1 dan TO 2 secara terpisah.
- requirements.txt: daftar pustaka Python.

FITUR UTAMA
- Dashboard ringkasan, grafik performa dan sebaran nilai.
- Analisis mendalam per sekolah dan perbandingan antarsekolah.
- Peringkat sekolah berdasarkan rata-rata tiga mata pelajaran (Bahasa Indonesia, Bahasa Inggris, Matematika).
- Peringkat sekolah untuk setiap mata pelajaran.
- Perbandingan TO 1 dan TO 2, termasuk perubahan nilai dan peringkat.
- Analisis indikator: ketercapaian, kategori soal, indikator, kompetensi, sub-elemen, dan elemen (sesuai kolom yang tersedia di Excel).
- Rekap kabupaten/kota, pemetaan sekolah otomatis dan koreksi manual.
- Data peserta didik, status pemrosesan file, dan ekspor laporan Excel.

CARA MENJALANKAN LOKAL
1. Install Python 3.10 atau lebih baru.
2. Buka terminal pada folder yang berisi app.py dan requirements.txt.
3. Jalankan: pip install -r requirements.txt
4. Jalankan: streamlit run app.py
5. Buka alamat lokal yang ditampilkan Streamlit.
6. Unggah workbook TO 1 pada uploader TO 1 dan workbook TO 2 pada uploader TO 2.

CARA HOSTING GRATIS (STREAMLIT COMMUNITY CLOUD)
1. Buat repository GitHub baru.
2. Unggah app.py dan requirements.txt ke repository.
3. Masuk ke https://share.streamlit.io/ lalu login menggunakan GitHub.
4. Pilih repository, branch, dan file utama app.py.
5. Klik Deploy.

CATATAN PENTING
- Unggah file Excel untuk masing-masing putaran pada kotak yang benar. Format sheet perlu mengikuti workbook sumber.
- Rata-rata gabungan tiga mapel dihitung dari rata-rata sekolah pada masing-masing mapel dengan bobot sama. Sekolah yang tidak memiliki data salah satu dari tiga mapel tidak dimasukkan ke peringkat gabungan, tetapi tetap muncul pada peringkat mapel yang datanya tersedia.
- Setiap workbook sebaiknya mewakili satu sekolah karena sheet indikator sekolah dilekatkan pada nama sekolah yang terdeteksi di workbook.
- Pemetaan manual kabupaten/kota dan unggahan tersimpan selama sesi aplikasi aktif. Simpan ekspor Excel sebagai arsip hasil pengolahan.
- Data peserta didik dapat memuat identitas pribadi. Batasi akses aplikasi, jangan publikasikan data siswa secara terbuka, dan gunakan hanya akun/lingkungan hosting yang disetujui instansi.
- Hosting gratis memiliki batas sumber daya dan dapat menidurkan aplikasi saat tidak digunakan. Untuk data resmi/sensitif, pastikan kebijakan keamanan dan persetujuan instansi sebelum mengunggah ke layanan cloud publik.
- Uji hasil terhadap seluruh workbook TO 1 dan TO 2 sebelum dipakai sebagai dasar laporan resmi.
