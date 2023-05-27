import inspect
from typing import Awaitable, Callable

from api.adapters import orm, redis_eventpublisher
from api.adapters.notifications import AbstractNotifications, EmailNotifications
from api.domain import events
from api.service_layer import handlers, messagebus, unit_of_work
import logging
import os
logger = logging.getLogger(__name__)


def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = None,
    notifications: AbstractNotifications = None,
    publish: Callable[[str, events.Event],
                      Awaitable] = redis_eventpublisher.publish,
) -> messagebus.MessageBus:
    if notifications is None:
        notifications = EmailNotifications()
    print(os.getenv("UOW"))
    if os.getenv("UOW") == "sqlalchemy":
        logger.info("Starting ORM")
        logger.info("Using UOW: %s", uow.__class__)
        if start_orm:
            orm.start_mappers()
        uow = unit_of_work.SqlAlchemyUnitOfWork()
    else:
        logger.info("Using UOW: %s", uow.__class__)
        uow = unit_of_work.MongoDBUnitOfWork()

    dependencies = {"uow": uow,
                    "notifications": notifications, "publish": publish}

    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies) for handler in event_handlers
        ]
        for event_type, event_handlers in handlers.EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in handlers.COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }
    return lambda message: handler(message, **deps)
