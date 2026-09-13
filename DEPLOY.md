# Deploy Winter Validator website

## Hiện trạng

- **Domain:** `validators.win`
  - Registrar: GoDaddy (mua 2022-01-07, hạn đến **2027-01-07**)
  - Nameservers hiện tại: `ns-cloud-c1..c4.googledomains.com` (Google Cloud DNS)
  - Quan trọng: **Google Domains đã bị tắt từ 2024** — NS này đang trỏ về Cloudflare sau migration tự động. Có thể domain đã nằm sẵn trong tài khoản Cloudflare của anh. **Check trước: login cloudflare.com → tìm validators.win**
- **Hosting cũ:** GoDaddy shared hosting `173.201.184.177` (secureserver.net) — web WordPress 2022 đã chết (home 404, SSL hết hạn). Bỏ, không renewal.
- **Web mới:** `website/winter-validator/index.html` — static 1 file, đã include BP key + hướng dẫn delegate.

## Option A — Cloudflare Pages (khuyên dùng, free)

1. Check anh có Cloudflare account chưa (xem bước "Hiện trạng" — domain có thể đã ở đó sau migration Google Domains)
2. Push `website/winter-validator/` lên GitHub repo (public hoặc private đều được)
3. Cloudflare Dashboard → Workers & Pages → Create → Pages → Connect to Git → chọn repo
4. Build settings: Framework = None, Build command = (trống), Output dir = `/`
5. Custom domain: Add domain → `validators.win` → nếu domain đã trong cùng account Cloudflare, DNS + SSL tự động, xong trong ~2 phút
6. Nếu domain KHÔNG trong Cloudflare: vào DNS cũ đổi NS về `xxx.ns.cloudflare.com` (Cloudflare sẽ chỉ exact pair), rồi làm tiếp bước 5

## Option B — GitHub Pages (cũng free, đơn giản hơn)

1. Tạo repo `winter-validator` (public), push thư mục `website/winter-validator/` (index.html nằm ở root)
2. Repo → Settings → Pages → Source: Deploy from branch → main / root
3. Custom domain: nhập `validators.win` → GitHub cho 4 A-record: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` + CNAME `www` → `<user>.github.io`
4. Vào DNS zone (Cloudflare/GoDaddy) sửa record trỏ `@` về 4 IP trên, bật "Enforce HTTPS" trong GitHub Pages

## Lưu ý khi đổi DNS

- Zone validators.win đang dùng Google Cloud DNS (ns-cloud-c1..c4) — nếu domain chưa migrate hẳn sang Cloudflare thì phải đổi NS ở **registrar GoDaddy** (My Products → DNS → Nameservers)
- TTL cũ của A-record GoDaddy có thể cache vài giờ — đổi xong chờ tối đa 24h, thường 5-30 phút
- Backup DNS records hiện tại trước khi đổi (dùng `dig` lưu lại) — an toàn hơn

## Việc anh cần quyết/làm

1. Deploy bằng Cloudflare Pages hay GitHub Pages? (em khuyên Cloudflare Pages)
2. Email liên hệ trên web: đang để `hello@validators.win` — cần tạo mailbox forward ở Cloudflare (free) hoặc đổi sang email khác
3. Commission thật bao nhiêu? (web đang ghi 5%)
4. Muốn em thêm khối gì nữa không: uptime status widget, link Auro/Cloria, trang riêng cho devnet key?

##Sau khi deploy xong
- Submit lên Mina ecosystem: Discord #staking, minaprotocol.com staking page (nếu còn nhận listing), các aggregator
- Tạo X/Twitter + GitHub org "WinterValidator" để có footprint khi người ta search "Winter Validator"
