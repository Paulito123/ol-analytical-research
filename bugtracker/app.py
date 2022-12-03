from util import get_active_set_ips
from asyncio import get_event_loop, run_coroutine_threadsafe, as_completed
from datetime import datetime, timedelta
from aiohttp import ClientSession
from time import sleep

validator_ip_refresh_rate_secs = 60
http_timeout = 5
active_set_ips = []
last_refresh = datetime.now() - timedelta(seconds=validator_ip_refresh_rate_secs + 1)
loop = get_event_loop()


def crawl_validators():
    global active_set_ips
    global last_refresh
    if last_refresh < (datetime.now() - timedelta(seconds=validator_ip_refresh_rate_secs)):
        last_refresh = datetime.now()
        active_set_ips = get_active_set_ips()
        print(f"Active set: {active_set_ips}")


async def scrape_metrics(session, url):
    print(f"Getting {url}")
    tout = http_timeout - 2
    try:
        async with session.get(url, timeout=tout) as resp:
            text = await resp.text()
    except Exception as e:
        text = f"{e}"
    return f"{url}: Got {len(text)} bytes"


async def build_tasks():
    crawl_validators()
    async with ClientSession() as session:
        tasks = [scrape_metrics(session, f"https://{ip}:9101/metrics") for ip in active_set_ips]
        for task in as_completed(tasks):
            print(await task)
    return "Done crawling."


# def evaluate_metrics(text, regex):



if __name__ == "__main__":
    print(f"{datetime.now()}")
    counter = 0
    keep_going = True
    loop = get_event_loop()
    while keep_going:
        resp = loop.run_until_complete(build_tasks())
        print(resp)
        print(f"{datetime.now()}")

        sleepy_time = 3
        print(f"sleeping {sleepy_time} secs")
        sleep(sleepy_time)

        counter += 1
        if counter == 3:
            keep_going = False
            
    print("loop closed!")
    loop.close()