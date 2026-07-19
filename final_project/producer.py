#!/usr/bin/env python3

import asyncio
import logging
import os
import sys

from aio_pika import connect, Message, DeliveryMode

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
ROUTING_KEY = 'test_routing_key'
EXCHANGE_NAME = ''

async def main() -> None:
    """Основная асинхронная функция продюсера."""
    dsn = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
    logger.info(f"Подключение к RabbitMQ: {RABBITMQ_HOST}:{RABBITMQ_PORT}")

    try:
        connection = await connect(dsn)
        logger.info("Соединение установлено")
    except Exception as e:
        logger.error(f"Не удалось подключиться к RabbitMQ: {e}")
        return

    async with connection:
        channel = await connection.channel()
        logger.info("Канал создан")

        _ = await channel.declare_queue(
            QUEUE_NAME,
            durable=True,
            auto_delete=False
        )
        logger.info(f"Очередь '{QUEUE_NAME}' объявлена (или уже существует)")

        messages = [
            "Hello, RabbitMQ!",
            "Это второе сообщение",
            "А это третье, с цифрой 3",
            "Последнее, четвёртое"
        ]

        for i, text in enumerate(messages, start=1):
            message = Message(
                body=text.encode('utf-8'),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type='text/plain',
                correlation_id=str(i),
                reply_to='producer_reply'
            )

            await channel.default_exchange.publish(
                message,
                routing_key=QUEUE_NAME
            )
            logger.info(f"Отправлено сообщение #{i}: '{text}' по ключу '{QUEUE_NAME}'")

        logger.info("Все сообщения отправлены. Завершаем продюсера.")

if __name__ == "__main__":
    asyncio.run(main())
