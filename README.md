# Hướng dẫn cài đặt Odoo trên linux
### B1: Chuẩn bị
1. Hệ điều hành ubuntu

### B2: Cài đặt docker and docker-compose

### B3: Cài đặt Odoo

### B4: Cấu hình cloudflared
1. Download cloudflared
```
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
```
2. Cài đặt cloudflared
```
sudo dpkg -i cloudflared.deb
```
3. Chạy chương trình autotunel
```
sudo ./autotunel/autotunel.sh
```
### B5: Cấu hình tailscalse
1. Cài đặt
```
curl -fsSL https://tailscale.com/install.sh | sh
```
2. Khởi chạy tailscale
Chạy lệnh sau và copy link đó dán vào browser để đăng ký device
```
sudo tailscale up
```
Cấu hình ssh
```
sudo tailscale status
sudo systemctl enable --now tailscaled
sudo tailscale set --ssh
```
