from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import random
from sys import exit, argv
import requests

def Usage():
    print(f"""
python prx.py <Timeout> <File Proxy> [Protocol]                              
Protocol: [ http | https | socks | 2 | h2 | 3128 ] 
""")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/604.1",
]

def ProxyConnector(proxy, port, protocol):
    try:
        # URLs to check against
        google_url = "https://www.google.com/"
        cloudflare_url = "https://www.cloudflare.com/"

        headers = {
            'User-Agent': random.choice(USER_AGENTS)
        }

        # Attempt to connect to Google first
        response_google = requests.get(
            google_url, 
            headers=headers, 
            proxies={protocol: f"{protocol}://{proxy}:{port}"}, 
            timeout=int(argv[1])
        )

        if response_google.status_code == 200:
            with open("live.txt", "a+") as f:
                f.write(f"{proxy}:{port}\n")
            result = f"\033[32mProxy Live: \033[33m{proxy}:{port} ({protocol}) - Google\033[0m"

            # If Google is accessible, check Cloudflare
            try:
                response_cloudflare = requests.get(
                    cloudflare_url, 
                    headers=headers, 
                    proxies={protocol: f"{protocol}://{proxy}:{port}"}, 
                    timeout=int(argv[1])
                )

                if response_cloudflare.status_code == 200:
                    with open("googleclf.txt", "a+") as f:
                        f.write(f"{proxy}:{port}\n")
                    result += f" | \033[32mBypassed Cloudflare\033[0m"
                else:
                    result += f" | \033[31mBlocked by Cloudflare\033[0m"
            except Exception as e:
                result += f" | \033[31mError with Cloudflare: {str(e)}\033[0m"
        else:
            raise ValueError("Google response not OK")

        return result

    except Exception as e:
        with open("dead.txt", "a+") as f:
            f.write(f"{proxy}:{port} ({protocol}) - {str(e)}\n")
        return f"\033[31mProxy Die: \033[33m{proxy}:{port} ({protocol}) - {str(e)}\033[0m"

def FileRead(file):
    if not file:
        print("\033[31mError: Proxy file not provided.\033[0m")
        exit(-1)

    if os.path.exists(file):
        with open(file, "r") as f:
            content = f.read().strip().split("\n")
        return content
    else:
        print(f"\033[31mFile: \033[33m'{file}'\033[0m does not exist in the current directory\033[0m")
        exit(-1)

def CheckFile(data):
    return all(":" in line for line in data)

def FilterProxies(proxies):
    return [proxy for proxy in proxies if proxy.endswith(":3128")]

def Main():
    # Logo()  # Remove or comment out the logo function call
    ct = FileRead(argv[2] if len(argv) > 2 else None)

    if not ct:
        print(f"\033[31mFile: \033[33m'{argv[2]}'\033[0m does not exist in the current directory\033[0m")
        exit(-1)

    if not CheckFile(ct):
        print("\033[31mTệp proxy của bạn có định dạng không đúng!\nCác định dạng cần phải giống như proxy:cổng trong mỗi dòng\033[0m")
        exit(-1)

    # Filter proxies to only include those with port 3128
    if argv[3] == "3128":
        ct = FilterProxies(ct)

    pool = ThreadPoolExecutor(max_workers=61)
    ftrs = []

    for proxy_line in ct:
        try:
            proxy, port = proxy_line.split(":")
            if argv[3] == "2":
                ftrs.append(pool.submit(ProxyConnector, proxy, port, "http"))
                ftrs.append(pool.submit(ProxyConnector, proxy, port, "https"))
            else:
                ftrs.append(pool.submit(ProxyConnector, proxy, port, argv[3]))
        except ValueError:
            print(f"\033[31mInvalid proxy format: \033[33m{proxy_line}\033[0m")
            continue

    for f in as_completed(ftrs):
        print(f.result())

    pool.shutdown()

if __name__ == "__main__":
    try:
        int(argv[1])
        str(argv[2])
        if argv[3] not in ["http", "https", "socks", "socks4", "socks5", "2", "h2", "3128"]:
            raise RuntimeError()
    except:
        Usage()
        exit(-1)
        
    Main()