import abc 
import asyncio 
import logging
# import smtplib 

#from src import config 

class AbstractNotifications(abc.ABC):
    @abc.abstractmethod 
    async def publish(self, destination, message):
        raise NotImplementedError

class EmailNotifications(AbstractNotifications):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.loop = asyncio.get_event_loop()
        self.server = None 

    async def send(self, destination, message):
        self.logger.log(logging.INFO, f"Sending email to {destination}")
        print(message)

    async def publish(self, destination, message):
        await self.send(destination, message)
