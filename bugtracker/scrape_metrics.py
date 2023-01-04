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
    return text


async def handle_text(text):
    ...


async def build_tasks():
    crawl_validators()
    async with ClientSession() as session:
        tasks = [scrape_metrics(session, f"http://{ip}:9101/metrics") for ip in active_set_ips]
        for task in as_completed(tasks):
            print(await task)
    return "Done crawling."


async def build_task_single_ip(ip, filename):
    async with ClientSession() as session:
        tasks = [scrape_metrics(session, f"http://{ip}:9101/metrics")]
        for task in as_completed(tasks):
            text = await task
            text_file = open(f"/home/user/projects/ol-analytical-research/assets/generated/{filename}", "w")
            n = text_file.write(text)
            text_file.close()
    return "Done."


if __name__ == "__main__":
    seconds_per_round = 5
    rounds = 20
    counter = 0
    loop = get_event_loop()

    # get current timestamp
    nu = datetime.now()
    # calculate start time by adding a minute
    starttijd = nu + timedelta(minutes=1)
    # floor it
    starttijd = starttijd - timedelta(seconds=nu.second, microseconds=nu.microsecond)
    # create filename
    filename = f"{starttijd}"[:19].replace(' ', '_').replace(':', '') + ".txt"
    # calculate sleeptime before starting
    sleeptime = starttijd - nu
    sleeptime = float(f"{sleeptime}"[-9:])
    print(f"sleeping {sleeptime} secs")
    sleep(sleeptime)

    while counter <= rounds:
        starttijd = starttijd + timedelta(seconds=seconds_per_round)
        filename = f"{starttijd}"[:19].replace(' ', '_').replace(':', '') + ".txt"
        
        resp = loop.run_until_complete(build_task_single_ip('99.145.200.98', filename))
        print(resp)

        sleeptime = starttijd - datetime.now()
        sleeptime = float(f"{sleeptime}"[-9:])
        print(f"sleeping {sleeptime} secs")
        sleep(sleeptime)

        counter += 1
            
    print("loop closed!")
    loop.close()
