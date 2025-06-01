# Stima_DiamondBot_tripleN by ANT Squad
Bot "tripleN" ini dirancang untuk bermain game Diamond dengan strategi greedy yang adaptif, memprioritaskan pengambilan diamond dan interaksi dengan bot lain berdasarkan kondisi permainan.

_Meet the squad :_
|NIM|Nama|Github|
|---|---|---|
|123140186|M. Arif Ardani|[Ardani](https://github.com/Kaizenix)|
|123140167|Nadya Shafwah Yusuf|[Nadya](https://github.com/Nadya-167-14)|
|123140157|Fadina Mustika Ratnaningsih|[Fadina](https://github.com/04-157-Fadina)|
## Algoritma Program
Algoritma Greedy yang digunakan pada bot ini :
1. **Greedy by Return (Waktu Kritis):** Prioritas utama untuk mengamankan poin di akhir permainan dengan segera kembali ke base jika waktu tersisa sedikit dan ada diamond.
2. **Greedy by Escape:** Efisien dalam melindungi diamond yang terkumpul dengan menghindari bot lawan yang mendekat.
3. **Greedy by Tackle:** Efisien dalam mendapatkan diamond dari lawan secara cepat dengan men-tackle bot yang membawa banyak diamond.
4. **Greedy by Return (Inventori Penuh):** Mengamankan poin dengan segera kembali ke base saat inventori diamond penuh.
5. **Greedy by Return (Inventori Hampir Penuh):** Efisien dalam melengkapi set diamond (mencari biru) atau kembali ke base jika inventori hampir penuh.
6. **Greedy by Red Button:** Mengatasi kelangkaan diamond dengan mengaktifkan generator diamond.
7. **Greedy by Diamond (Densitas Terbaik):** Efisien dalam pengumpulan diamond dengan memprioritaskan yang paling menguntungkan (nilai/jarak) dan yang terdekat dari base.
8. **Greedy by Exploration (Unvisited Cells):** Strategi fallback untuk menjelajahi peta dan menemukan sumber daya baru secara efisien dalam jangka panjang.

## Penggunaan Program
- Game engine yang digunakan adalah :

  `https://github.com/haziqam/tubes1-IF2211-game-engine`

- Bot yang digunakan :

  `https://github.com/Nadya-167-14/Stima_DiamondBot_tripleN`

- Setelah menjalankan game engine, pemain bisa mengakses bot dengan membuka file src dan mengakses cmd dari path folder src tersebut.
- Untuk menjalankan satu bot, pemain bisa memasukkan command. Misalnya seperti ini (email dan password bebas, tidak harus email nyata, yang penting format sama) :

  `python main.py --logic tripleN --email=antsquad@gmail.com --name=antsquad --password=gacorabis --team etimo`

- Jika ingin menggunakan lebih dari satu bot, pemain bisa membuat file run-bots.bat atau run-bots.sh
- Setelah file dibuat, maka pemain bisa memasukkan command :

  `.\run-bots.bat`

  atau

  `.\run-bots.sh`
