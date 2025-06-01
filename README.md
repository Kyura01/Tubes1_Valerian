
# Tugas Besar 1 Strategi Algoritma - Valerian

- Ahmad Ali Mukti 123140155

- Falent Antonius Panjaitan 123140124

- Nayla Devina Febrianti 123140061


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# 💎 Etimo Diamonds 2


## Deskripsi Umum

Tugas Besar 1 Strategi Algoritma ini bertujuan untuk mengimplementasikan bot pada permainan Diamonds. Permainan Diamonds merupakan permainan sederhana yang memiliki objektif bagi pemain untuk mendapatkan Diamonds sebanyak-banyaknya pada papan permainan.

Bot yang dibuat akan menggunakan algoritma Greedy dengan tujuan utama mendapatkan Diamond sebanyak-banyaknya agar dapat memenangkan permainan.

## Penjelasan Algoritma
Poin penting pada implementasi algoritma greedy pada bot kami adalah sebagai berikut, dengan fokus pada pengambilan keputusan yang efisien untuk memaksimalkan skor


### 1. Prioritas Utama: Mengamankan Skor dengan Kembali ke Markas (Greedy by Strategic Time-Constrained Return)
Bot akan **mengutamakan** keputusan untuk kembali ke markas jika salah satu kondisi berikut terpenuhi, mengesampingkan sementara pencarian diamond lebih lanjut:
*   Sisa waktu permainan di bawah ambang batas kritis (`URGENCY_TIMER_LIMIT`) dan bot sedang membawa diamond.
*   Inventaris diamond bot sudah penuh (`robot_stats.diamonds >= robot_stats.inventory_size`).
*   Bot telah mengumpulkan sejumlah diamond yang dianggap cukup (`CASH_OUT_THRESHOLD`) DAN tidak ada diamond lain yang terdeteksi dalam radius dekat (`NEARBY_RADIUS`) dari posisi bot saat ini.

### 2. Jika Kondisi Kembali Tidak Terpenuhi: Mencari Diamond Paling Efisien (Greedy by Value Combination Distance)
Apabila tidak ada urgensi untuk kembali ke markas seperti yang dijelaskan pada poin pertama, bot akan **memilih aksi** untuk mencari dan menuju diamond yang menawarkan rasio `nilai_poin / jarak_efektif_ke_diamond` terbaik. Ini memastikan bot tidak hanya mengejar diamond bernilai tinggi yang sangat jauh atau diamond terdekat yang nilainya kecil, melainkan mencari keseimbangan optimal. Kalkulasi "jarak efektif" ini secara otomatis mempertimbangkan rute terpendek, termasuk melalui portal teleportasi jika lebih menguntungkan. Hanya diamond yang muat dalam sisa kapasitas inventaris yang dipertimbangkan.

### 3. Fallback Jika Tidak Ada Target Diamond yang Layak
Jika dalam proses pencarian tidak ditemukan diamond yang menguntungkan berdasarkan kriteria rasio di atas (misalnya, tidak ada diamond yang terlihat, tidak ada yang muat di inventaris, atau semua menghasilkan rasio rendah), bot akan **secara default** bergerak menuju markasnya (karena `target_destination` diinisialisasi ke `robot_stats.base` dan tidak diubah jika tidak ada `optimal_gem_location` yang ditemukan). Bot ini tidak memiliki logika untuk mengejar diamond yang sangat jauh secara membabi buta jika rasionya tidak baik, atau untuk menekan tombol reset.

### 4. Optimalisasi Rute Sepanjang Perjalanan
Dalam setiap keputusan pergerakan, baik menuju diamond (seperti pada poin 2) maupun menuju markas (seperti pada poin 1 atau 3), bot akan selalu **memanfaatkan** fungsi `determine_optimal_route`. Fungsi ini akan memilih jalur terpendek, baik itu jalur langsung maupun jalur yang melibatkan penggunaan portal teleportasi, untuk mencapai tujuannya.


## Installing Dependencies 🔨

1. Clone this repository and move to the root of this project's directory

    ```
    git clone https://github.com/Kyura01/Tubes1_Valerian
    cd ./tubes1-IF2110-bot-starter-pack
    ```

2. Install dependencies

    ```
    pip install -r requirements.txt
    ```

## How to Run 💻

1. To run one bot

    ```
    python main.py --logic Random --email=your_email@example.com --name=your_name --password=your_password --team etimo
    ```

2. To run multiple bots simultaneously

    For Windows

    ```
    ./run-bots.bat
    ```

    For Linux / (possibly) macOS

    ```
    ./run-bots.sh
    ```

    Before executing the script, make sure to change the permission of the shell script to enable executing the script (for linux/macOS)

    ```
    chmod +x run-bots.sh
    ```

#### Note:

-   If you run multiple bots, make sure each emails and names are unique
-   The email could be anything as long as it follows a correct email syntax
-   The name, and password could be anything without any space



