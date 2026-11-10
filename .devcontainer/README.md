# GitHub Codespaces cho HONOR X7d 4G

Workspace này chỉ dùng để **đọc và so sánh thông tin firmware**. Không chạy
exploit, không flash, không thay đổi thiết bị, không tự tải lên firmware.

## Tạo workspace

1. Mở repository `tuanviet200777-lab/ghostlock-app` trên GitHub.
2. Chuyển sang nhánh `tools/honor-x7d-firmware-readonly-analysis`.
3. Bấm **Code → Codespaces → Create codespace on this branch**.
4. Codespaces đọc `.devcontainer/devcontainer.json` và chuẩn bị Python,
   Rust, công cụ archive/firmware. Sau khi tạo xong, hai bộ unit test Python
   được chạy qua `postCreateCommand`.

**Lưu ý:** PR #3 chứa cấu hình này nhưng chưa merge vào `main`. Tạo Codespace
trên nhánh nêu trên để dùng ngay. Bạn có thể bị GitHub tính phí hoặc giới hạn
thời gian/dung lượng Codespaces tùy tài khoản.

## Lưu firmware ngoài Git

Dữ liệu của Codespace có đường dẫn tương ứng:

- `/workspaces/ghostlock-private/firmware/`: đặt bản sao firmware đã xem xét.
- `/workspaces/ghostlock-private/reports/`: lưu báo cáo JSON chỉ dùng nội bộ.

Hai thư mục được tạo **ngoài cây repository** để lệnh `git add .` không
vô tình đưa chúng vào PR. Đường dẫn `/workspaces` tồn tại qua việc rebuild
devcontainer nhưng **không phải bản sao lưu bảo đảm lâu dài**; xóa Codespace
hoặc chính sách lưu trữ có thể làm mất dữ liệu.

Không đưa `userdata.img`, `metadata.img`, `cache.img`, phân vùng khóa,
dump có dữ liệu cá nhân hoặc tài liệu bị giới hạn quyền chia sẻ vào Codespace.
Đối với firmware hãng, cần xem xét quyền sử dụng và phân phối.

## Phân tích offline

Sau khi bạn tải **những file được phép phân tích** vào thư mục firmware của
Codespace, mở terminal (đang ở gốc repo) và chạy:

```bash
python3 tools/inspect_honor_firmware.py \
  --boot "/workspaces/ghostlock-private/firmware/boot(2).img" \
  --vendor-boot "/workspaces/ghostlock-private/firmware/vendor_boot(2).img" \
  --version-tag "/workspaces/ghostlock-private/firmware/version_by_CI(1).tag" \
  --out "/workspaces/ghostlock-private/reports/x7d-226-offline.json"
```

Kết quả gồm checksum SHA-256, định dạng ảnh và **chuỗi phiên bản kernel tìm
thấy trong boot image**. Không coi đó là `uname -r` đo trực tiếp trên điện
thoại. Bản MagicOS được chủ máy xác nhận là **9.0.0.226**. Không sử dụng
báo cáo GitHub đã gửi nhầm trước đó làm thông tin nhận diện thiết bị.

Nếu có ADB JSON được đọc từ điện thoại **của bạn** bằng công cụ chỉ đọc
`tools/probe_honor_x7d_4g.py` trên máy tính riêng, bạn có thể kiểm tra và
sao chép một bản đã rà soát vào thư mục riêng trên Codespace rồi so sánh bằng
tùy chọn `--device-report`. Codespaces trên cloud **không trực tiếp thấy
cổng USB** của điện thoại cắm vào PC thông thường.

## Kiểm tra môi trường

```bash
python3 --version
cargo --version
python3 -m unittest discover -s tools -p 'test_inspect_honor_firmware.py' -v
python3 -m unittest discover -s tools -p 'test_probe_honor_x7d_4g.py' -v
```

Các bài kiểm thử được dùng để phát hiện lỗi trong công cụ chỉ đọc. Một bài
test thành công không chứng minh điện thoại tương thích hay root được.

Bản Rust extractor `tools/extract_rs` đã có trong repo để phục vụ nghiên
cứu offline; setup Codespaces **không tự build hoặc chạy khai thác kernel**.

## Mức độ hoàn tất

- Đã commit cấu hình Dev Container, Dockerfile, startup script và GitHub
  Actions CI cho Python.
- Chưa trực tiếp tạo Codespace trên tài khoản của bạn: phải mở Codespaces
  trên GitHub theo bước trên.
- Chưa có firmware nhị phân được đẩy vào repo, và chưa kết nối điện thoại.
- Giữ nhánh `main` và toàn bộ exploit/native code nguyên trạng.
