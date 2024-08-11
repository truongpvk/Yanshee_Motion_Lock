# Khoá tầm nhìn và khoảng cách tới vật thể
Robot được lập trình để có thể di chuyển tới vật phẩm ở một khoảng cách, góc độ và độ lệch nhất định. Điều này được sử dụng để hỗ trợ cho nhiệm vụ lấy vật thể sau này.

## Cập nhật
`11/8/2024`
Chỉnh sửa lại các trình bày của code + Thêm tính năng tự động tìm kiếm vật thể bằng cách quay xung quanh.

## Các tệp chương trình
Các tệp chương trình có thể tìm thấy ở folder `src`:
- `main.py`: chứa code chính của chương trình
- `turn_on_stream.py`: kích hoạt luồng stream của robot, chạy tệp này vào lần đầu tiên trước khi chạy `main`
- `offset_processing.py`: chứa các hàm xử lý tình huống vật thể lệch trái hoặc phải
- `distance_processing.py`: chứa các hàm xử lý tình huống vật thể quá xa hoặc quá gần
- `angle_processing.py`: chứa các hàm xử lý tình huống robot lệch góc nhìn với vật thể
- `motion_processing.py`: chứa các hàm xử lý chuyển động cho robot