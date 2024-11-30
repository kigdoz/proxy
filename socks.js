const axios = require('axios');
const fs = require('fs');

const proxies = [];
const output_file = 'proxy.txt';

if (fs.existsSync(output_file)) {
  fs.unlinkSync(output_file);
  console.log(`'${output_file}' đã xóa bỏ.`);
}

const raw_proxy_sites = [ 
'http://worm.rip/socks5.txt',
'https://spys.me/proxy.txt', 
'https://spys.me/socks.txt',
'https://proxy-list.download/api/v1/get?type=socks5',
'https://proxyspace.pro/socks5.txt',
'https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5',
'https://api.openproxylist.xyz/socks5.txt',
"https://daudau.org/api/socks.txt",
];
async function fetchProxies() {
  for (const site of raw_proxy_sites) {
    try {
      const response = await axios.get(site);
      const lines = response.data.split('\n');
      for (const line of lines) {
        if (line.includes(':')) {
          const [ip, port] = line.split(':', 2);
          proxies.push(`${ip}:${port}`);
        }
      }
    } catch (error) {
      console.error(`Không thể truy xuất proxy từ ${site}: ${error.message}`);
    }
  }

  fs.writeFileSync(output_file, proxies.join('\n'));
  console.log(`Proxy đã được truy xuất và lưu trữ thành công trong ${output_file}`);
}

fetchProxies();
