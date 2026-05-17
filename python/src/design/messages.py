import enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Type


class MessageType(enum.Enum):
    TELEGRAM = enum.auto()
    MATTERMOST = enum.auto()
    SLACK = enum.auto()


@dataclass
class JsonMessage:
    message_type: MessageType
    payload: str


@dataclass
class ParsedMessage:
    """There is no need to describe anything here."""


class ParserNotFoundError(Exception):
    pass


class Parser(ABC):
    @abstractmethod
    def parse(self, message: JsonMessage) -> ParsedMessage:
        "Method for parsing messages"
        pass


class ParserFactory:
    "Parser factory"

    __registry = {}

    @staticmethod
    def register(message_type: MessageType):
        def decorator(parser_class: Type[Parser]):
            ParserFactory.__registry[message_type] = parser_class
            return parser_class

        return decorator

    @staticmethod
    def get_parser(message_type: MessageType) -> Parser:
        parser_class = ParserFactory.__registry[message_type]
        return parser_class()


@ParserFactory.register(message_type=MessageType.TELEGRAM)
class TelegramParser(Parser):
    def parse(self, message: JsonMessage) -> ParsedMessage:
        "Telegram parser"
        print("Telegram message parsed: "
              "\n\ttype: {}\n\tpayload: {}".format(message.message_type, message.payload))
        return ParsedMessage()


@ParserFactory.register(message_type=MessageType.MATTERMOST)
class MattermostParser(Parser):
    def parse(self, message: JsonMessage) -> ParsedMessage:
        "Telegram parser"
        print("Mattermost message parsed: "
              "\n\ttype: {}\n\tpayload: {}".format(message.message_type, message.payload))
        return ParsedMessage()


@ParserFactory.register(message_type=MessageType.SLACK)
class SlackParser(Parser):
    def parse(self, message: JsonMessage) -> ParsedMessage:
        "Telegram parser"
        print("Slack message parsed: "
              "\n\ttype: {}\n\tpayload: {}".format(message.message_type, message.payload))
        return ParsedMessage()


if __name__ == "__main__":
    pf = ParserFactory()
    parser = pf.get_parser(MessageType.TELEGRAM)
    res1 = parser.parse(JsonMessage(MessageType.TELEGRAM, "telegram message"))
    print(type(res1))

    slack_parser = pf.get_parser(MessageType.SLACK)
    res2 = slack_parser.parse(JsonMessage(MessageType.SLACK, "slack message"))
    print(type(res2))

    # invalid_parser = pf.get_parser("slkjdf") # type: ignore
