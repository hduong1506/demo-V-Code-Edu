// KHO DỮ LIỆU BÀI HỌC & BÀI TẬP PYTHON — DỄ DÀNG THÊM/SỬA/NÂNG CẤP SAU NÀY
window.VCODE_LESSONS = [
  {
    id: "py-01",
    order: 1,
    title: "Bài 1: Biến, Kiểu dữ liệu & Nhập xuất (input / print)",
    level: "Cơ bản • Tin học 10",
    duration: "15 phút",
    summary: "Làm quen cách khai báo biến, đọc dữ liệu số nguyên bằng int(input()) và hiển thị kết quả ra màn hình.",
    theory: "Trong Python, ta không cần khai báo kiểu dữ liệu trước. Dùng hàm <code>input()</code> để nhận chuỗi từ bàn phím, bọc trong <code>int(...)</code> để chuyển thành số nguyên và dùng <code>print(...)</code> để xuất kết quả.",
    starter: "# Bài 1: Nhập cạnh N và tính chu vi hình vuông\nn = int(input())\nchu_vi = n * 4\nprint(chu_vi)",
    testCases: [{ input: "5", expected: "20" }, { input: "12", expected: "48" }]
  },
  {
    id: "py-02",
    order: 2,
    title: "Bài 2: Cấu trúc Rẽ nhánh (if / elif / else)",
    level: "Cơ bản • Tin học 10",
    duration: "20 phút",
    summary: "Xây dựng chương trình ra quyết định theo điều kiện và phân loại học lực theo thang điểm.",
    theory: "Câu lệnh <code>if điều_kiện:</code> kết thúc bằng dấu hai chấm <code>:</code> và các lệnh bên trong phải thụt lề 4 khoảng trắng. Toán tử so sánh bằng là <code>==</code>, chia lấy dư là <code>%</code>.",
    starter: "# Bài 2: Phân loại học lực theo điểm trung bình (0 - 10)\ndiem = int(input())\nif diem >= 8:\n    print('Gioi')\nelif diem >= 6:\n    print('Kha')\nelse:\n    print('Can co gang')",
    testCases: [{ input: "9", expected: "Gioi" }, { input: "7", expected: "Kha" }, { input: "4", expected: "Can co gang" }]
  },
  {
    id: "py-03",
    order: 3,
    title: "Bài 3: Vòng lặp for & Tính tổng có điều kiện",
    level: "Trung bình • Tin học 10 & 11",
    duration: "25 phút",
    summary: "Sử dụng vòng lặp for kết hợp hàm range() để duyệt dãy số và cộng dồn các số chẵn từ 1 đến N.",
    theory: "Hàm <code>range(1, n + 1)</code> tạo dãy số liên tiếp từ 1 đến đúng n. Khi kết hợp <code>for</code> với <code>if</code> bên trong, ta giải được hầu hết bài toán đếm và tính tổng cơ bản.",
    starter: "# Bài 3: Tính tổng các số chẵn từ 1 đến N\nn = int(input())\ntong = 0\nfor i in range(1, n + 1):\n    if i % 2 == 0:\n        tong = tong + i\nprint(tong)",
    testCases: [{ input: "6", expected: "12" }, { input: "10", expected: "30" }, { input: "1", expected: "0" }]
  },
  {
    id: "py-04",
    order: 4,
    title: "Bài 4: Thuật toán Giai thừa & Cầu nối Python Tiếng Việt",
    level: "Nâng cao • Ôn luyện HSG",
    duration: "25 phút",
    summary: "Tính tích N! bằng vòng lặp tích lũy và làm quen cú pháp Python Tiếng Việt thân thiện.",
    theory: "Để tính tích (giai thừa), biến kết quả ban đầu phải khởi tạo bằng <code>1</code> (không được đặt bằng 0). Em cũng có thể thử gõ <code>lap_voi</code>, <code>in_ra</code> ở chế độ Python Tiếng Việt!",
    starter: "# Bài 4: Tính giai thừa N! = 1 * 2 * ... * N\nn = int(input())\ngt = 1\nfor i in range(1, n + 1):\n    gt = gt * i\nprint(gt)",
    testCases: [{ input: "5", expected: "120" }, { input: "3", expected: "6" }, { input: "1", expected: "1" }]
  }
];
