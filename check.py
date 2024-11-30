import sys
import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
import time
import concurrent.futures
import os
import resource

soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))

def check_arguments():
    if len(sys.argv) < 4:
        print("Usage: python check.py <input_file> <output_file> <protocol>")
        sys.exit(1)
    return sys.argv[1], sys.argv[2], sys.argv[3]

pure_proxies, good_proxies, protocol = check_arguments()

async def check_proxy(session, proxy_address):
    url = 'http://httpbin.org/ip'
    try:
        async with session.get(url, timeout=20) as response:
            if response.status == 200:
                print(f"Success: {proxy_address}")
                return True, proxy_address
            else:
                print(f"Error ({proxy_address}): HTTP {response.status} {response.reason}")
                return False, proxy_address
    except asyncio.TimeoutError:
        print(f"Timeout: {proxy_address}")
    except aiohttp.ClientResponseError as e:
        print(f"Response Error ({proxy_address}): {e.status} {e.message}")
    except aiohttp.ClientConnectorError as e:
        print(f"Connection Error ({proxy_address}): {str(e)}")
    except aiohttp.InvalidURL:
        print(f"Invalid URL Error ({proxy_address}): The proxy URL is not valid")
    except aiohttp.ServerDisconnectedError:
        print(f"Server Disconnected ({proxy_address}): The proxy server closed the connection unexpectedly")
    except Exception as e:
        print(f"Unexpected Error ({proxy_address}): {str(e)}")
    return False, proxy_address

async def check_proxy_chunk(proxies):
    success_proxies = set()
    semaphore = asyncio.Semaphore(100)

    async def check_proxy_wrapper(proxy):
        async with semaphore:
            try:
                connector = ProxyConnector.from_url(f'{protocol}://{proxy}')
                async with aiohttp.ClientSession(connector=connector) as session:
                    success, address = await check_proxy(session, proxy)
                    if success:
                        success_proxies.add(address)
            except Exception as e:
                print(f"Unexpected error with proxy {proxy}: {str(e)}")

    await asyncio.gather(*(check_proxy_wrapper(proxy) for proxy in proxies))
    return success_proxies

def process_chunk(chunk):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(check_proxy_chunk(chunk))

def main():
    with open(pure_proxies, 'r') as file:
        proxies = [line.strip() for line in file]

    total = len(proxies)
    chunk_size = 1000
    chunks = [proxies[i:i+chunk_size] for i in range(0, total, chunk_size)]

    success_proxies = set()
    checked = 0

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
        for future in concurrent.futures.as_completed(futures):
            chunk_results = future.result()
            success_proxies.update(chunk_results)
            checked += chunk_size
            print(f"Checked: {min(checked, total)}/{total} | Success: {len(success_proxies)}")

    end_time = time.time()
    print(f"\nTotal time taken: {end_time - start_time:.2f} seconds")

    print(f"\nSaved {len(success_proxies)} good proxies to {good_proxies}")
    with open(good_proxies, 'w') as file:
        for proxy in success_proxies:
            file.write(f"{proxy}\n")

if __name__ == "__main__":
    main()