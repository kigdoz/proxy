import concurrent.futures
import requests
import os

os.system("color 0")
os.system("cls" if os.name == "nt" else "clear")

def kiem_tra_proxy(proxy, timeout):
    try:
        response = requests.get('http://103.195.236.167/a.html', proxies={'http': proxy, 'https': proxy}, timeout=timeout)
        if response.status_code == 200:
            return proxy
    except:
        pass
    return None

def loc_proxy_trung(proxies):
    proxies_uniques = set(proxies)
    return list(proxies_uniques)

def tai_danh_sach_proxy(ten_file):
    if not os.path.isfile(ten_file):
        print(f"  File '{ten_file}' không tồn tại. Vui lòng nhập lại.")
        return tai_danh_sach_proxy(input("  Nhập tên file chứa danh sách proxy: "))
    with open(ten_file) as f:
        return [line.strip() for line in f.readlines()]

def luu_danh_sach_proxy(proxies, ten_file):
    with open(ten_file, 'w') as f:
        f.write('\n'.join(proxies))

def luu_danh_sach_proxy_loc(proxies, ten_file):
    check_file = "check-" + ten_file
    with open(check_file, 'w') as f:
        f.write('\n'.join(proxies))

banner = """
    --------------------------------------------
    |        CHƯƠNG TRÌNH KIỂM TRA PROXY       |
    |             Copyright Đậu Đậu            |
    --------------------------------------------
"""

def main():
    print(banner)

    ten_file = input("\n  Nhập tên file chứa danh sách proxy: ")

    proxies = tai_danh_sach_proxy(ten_file)

    print("================================================")
    print("  1. Lọc các proxy trùng nhau")
    print("  2. Kiểm tra proxy hoạt động")

    choice = input("  Nhập lựa chọn: ")

    if choice == "1":
        proxies_uniques = loc_proxy_trung(proxies)
        luu_danh_sach_proxy(proxies_uniques, ten_file)
        print("================================================")
        print("\n  Kết quả lọc proxy trùng nhau")
        print(f'  Tổng số proxy đã tìm thấy: {len(proxies)}')
        print(f'  Tổng số proxy còn lại: {len(proxies_uniques)}')
        input()
    elif choice == "2":
        timeout = int(input("  Nhập timeout (số giây): "))
        print("\n  Đang kiểm tra proxy. Vui lòng đợi...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(lambda proxy: kiem_tra_proxy(proxy, timeout), proxies))

        proxies_loc = [proxy for proxy in results if proxy is not None]
        luu_danh_sach_proxy_loc(proxies_loc, ten_file)
        print("================================================")
        print("\n  Kết quả kiểm tra proxy hoạt động")
        print(f'  Tổng số proxy đã tìm thấy: {len(proxies)}')
        print(f'  Tổng số proxy hoạt động: {len(proxies_loc)}')
        input()
    else:
        print("================================================")
        print("\n  Lựa chọn không hợp lệ. Đã thoát chương trình.")
        input()

if __name__ == "__main__":
    main()
