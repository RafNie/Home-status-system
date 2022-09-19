import asyncio
import logging
from asyncio_mqtt import Client, MqttError
from aiohttp import web
import ssl
from pathlib import Path
import json
import datetime

ROOT = Path(__file__).parent
logger = logging.getLogger(__name__)

door_status = ""
battery_low = False
last_report_time = ""

status_map = {'open':'Drzwi otwarte','closed':'Drzwi zamknięte'}


def process_door_status(message):
    data = json.loads(message.payload.decode())
    global door_status
    global battery_low
    global last_report_time
    if data["contact"] is True :
        door_status = "closed"
    else:
        door_status = "open"
    battery_low = data["battery_low"]
    now = datetime.datetime.now()
    format = "%d/%m/%Y %H:%M:%S"
    last_report_time = now.strftime(format)
    print("Message processed")

async def mqtt():
    while True:
        try:
            logger.info("Connecting to MQTT")
            async with Client("192.168.0.138") as client:
                logger.info("Connection to MQTT open")
                async with client.unfiltered_messages() as messages:
                    await client.subscribe("zigbee2mqtt/test_dev")
                    async for message in messages:
                        logger.info("Message %s %s", message.topic, message.payload.decode())
                        process_door_status(message)
                # await asyncio.sleep(2)
        except MqttError as e:
            logger.error("Connection to MQTT closed: " + str(e))
        except Exception:
            logger.exception("Connection to MQTT closed")
        await asyncio.sleep(3)



async def index(request):
    content = open(str(ROOT / 'static' / 'index.html')).read()
    return web.Response(content_type='text/html', text=content)

async def status(request):
    content = ''
    if len(last_report_time) > 0 :
        text = status_map[door_status]+'<br>'+last_report_time
        if battery_low :
            text = text+'<br> Słaba bateria'
        data = {"state":door_status, "text":text}
        content = json.dumps(data)
    logger.info('Ststus response: %s', content)
    return web.Response(content_type='text/html', text=content)

runners = []

async def start_site(app, address='localhost', port=8080, ssl_context = None):
    runner = web.AppRunner(app)
    runners.append(runner)
    await runner.setup()
    site = web.TCPSite(runner, address, port, ssl_context=ssl_context)
    await site.start()




def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    app = web.Application()
    app.router.add_get('/', index)
    app.router.add_get('/index', index)
    app.router.add_get('/status', status)
    app.router.add_static('/static/', path=ROOT / 'static', name='static')
    
    loop = asyncio.get_event_loop()
    loop.create_task(start_site(app, address='0.0.0.0'))
    loop.create_task(mqtt())
    logging.info('Applications created')

    try:
        loop.run_forever()
    except:
        pass
    finally:
        for runner in runners:
            loop.run_until_complete(runner.cleanup())


if __name__ == "__main__":
    main()
