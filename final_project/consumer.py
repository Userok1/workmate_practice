#!/usr/bin/env python3

import asyncio
import logging
import os
import sys
import signal

from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')

QUEUE_NAME = 'test_queue'
PREFETCH_COUNT = 1

async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        body = message.body.decode('utf-8')
        logger.info(
            f"Получено сообщение: '{body}' | "
            f"correlation_id={message.correlation_id}, "
            f"routing_key={message.routing_key}, "
            f"delivery_tag={message.delivery_tag}"
        )

        await asyncio.sleep(0.5)
        logger.info(f"Сообщение '{body}' обработано")


async def main() -> None:
    dsn = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
    logger.info(f"Подключение к RabbitMQ: {RABBITMQ_HOST}:{RABBITMQ_PORT}")

    stop_event = asyncio.Event()

    def signal_handler() -> None:
        logger.info("Получен сигнал завершения, останавливаем consumer...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        connection = await connect_robust(dsn)
        logger.info("Соединение установлено")
    except Exception as e:
        logger.error(f"Не удалось подключиться: {e}")
        return

    async with connection:
        channel = await connection.channel()
        logger.info("Канал создан")

        await channel.set_qos(prefetch_count=PREFETCH_COUNT)
        logger.info(f"QoS установлен: prefetch_count={PREFETCH_COUNT}")

        queue = await channel.declare_queue(
            QUEUE_NAME,
            durable=True,
            auto_delete=False
        )
        logger.info(f"Очередь '{QUEUE_NAME}' объявлена, начинаем потребление")

        consumer_tag = await queue.consume(on_message, no_ack=False)
        logger.info("Consumer запущен и ожидает сообщения...")

        await stop_event.wait()
        logger.info("Consumer завершает работу (отменяем подписку)")

        await queue.cancel(consumer_tag)
        logger.info("Подписка отменена")


if __name__ == "__main__":
    asyncio.run(main())
