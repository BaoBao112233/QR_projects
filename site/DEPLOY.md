# Deploy / chống out-RAM

Đây là **site tĩnh** — không cần app server. Lỗi out-RAM trước đây đến từ:
1. Ảnh PNG quá nặng (224MB) → mỗi request đọc vào page-cache, traffic cao làm phình RAM.
   → **Đã xử lý**: nén PNG/JPG → WebP + resize 1080px, còn **~32MB** (giảm 86%).
2. `python -m http.server` / server Node tự viết: đơn luồng, đệm cả file vào RAM,
   không có cache header → mỗi khách tải lại toàn bộ ảnh.
   → Dùng web server tĩnh chuyên dụng bên dưới.

## Cách 1 — Caddy (khuyến nghị, đơn giản nhất)
```bash
cd site
caddy run --config ./Caddyfile     # sửa your-domain.com trong Caddyfile trước
```
RAM gần như cố định dù bao nhiêu lượt truy cập, tự động HTTPS + nén + cache.

## Cách 2 — Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /duong/dan/toi/site;        # trỏ tới thư mục site/
    index index.html;

    sendfile on;                      # stream thẳng từ disk, không qua RAM app
    tcp_nopush on;
    gzip on;
    gzip_types text/css application/javascript application/json;

    location /data/   { expires 1y; add_header Cache-Control "public, immutable"; }
    location /assets/ { expires 1y; add_header Cache-Control "public, immutable"; }
    location ~* \.(css|js)$ { expires 1d; }
    location ~* \.html$ { add_header Cache-Control "public, max-age=0, must-revalidate"; }
}
```
`sendfile on` cho nhân hệ điều hành stream file thẳng ra socket — RAM không tăng theo traffic.

## Nếu BẮT BUỘC chạy bằng Python
Đừng dùng `http.server` cho production. Đặt nginx/Caddy phía trước, hoặc tối thiểu dùng
một static server có streaming + nhiều worker (vd `uvicorn`/`gunicorn` phục vụ Starlette
`StaticFiles`). Nhưng với site tĩnh thì Caddy/nginx là lựa chọn nhẹ và đúng nhất.

## Khi cập nhật ảnh mới
1. Bỏ ảnh gốc vào `site/data/...`
2. `python optimize_images.py`   (nén + đổi tham chiếu JSON sang .webp)
3. `python generate_site.py`     (build lại trang sản phẩm)
