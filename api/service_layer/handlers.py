from dataclasses import asdict
from api.utils.hashoor import verify_password 
from api.domain import events, models, commands
from api.adapters import redis_eventpublisher
from api.service_layer import unit_of_work
from api.config import get_redis_host_and_port
import redis


# Initialize a Redis client
r = redis.Redis(host=get_redis_host_and_port()["host"],
                port=get_redis_host_and_port()["port"],
                db=0, decode_responses=True)

# User handlers
async def create_user_handler(cmd: commands.CreateUser,
                              uow: unit_of_work.AbstractUnitOfWork):
    try: 
        command_dict = asdict(cmd)
        print(command_dict)
        user = models.User(email=command_dict["email"],
                           password=command_dict["password"],
                           dni=command_dict["dni"],
                           name=command_dict["name"],
                           last_name=command_dict["last_name"])

    except TypeError:
        raise TypeError("Invalid user data")
    async with uow:
        await uow.users.add(user)
        await uow.commit()
    await redis_eventpublisher.publish(channel="users", event="UserCreated",
                                       data=asdict(user))
    return True        

async def get_user_handler(cmd: commands.GetUser,
                           uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        user = await uow.users.get(cmd.id)
        await uow.commit()
        return user

async def delete_user_handler(cmd: commands.DeleteUser,
                              uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        user = await uow.users.get(cmd.id)
        if user is None:
            raise ValueError("User not found")
        await uow.users.delete(user)
        await uow.commit()
        return True

# Auth and registering 
async def authenticate_user(cmd: commands.AuthenticateUser,
                            uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        user = await uow.users.get_by_email(cmd.email)
        if user is None:
            raise ValueError("User not found")
        if not verify_password(cmd.password, user.password):
            raise ValueError("Invalid password")
        return user

# Poll handlers 
async def create_poll_handler(cmd: commands.CreatePoll,
                              uow: unit_of_work.AbstractUnitOfWork):
    try: 
        poll = models.Poll(**asdict(cmd))
    except TypeError:
        raise TypeError("Invalid poll data")
    async with uow:
        await uow.polls.add(poll)
        await uow.commit()
    await redis_eventpublisher.publish(channel="polls", event="PollCreated",
                                       data=asdict(poll))
    return True        

async def get_poll_handler(cmd: commands.GetPoll,
                           uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        poll = await uow.polls.get(cmd.id)
        await uow.commit()
        return poll

async def delete_poll_handler(cmd: commands.DeletePoll,
                              uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        poll = await uow.polls.get(cmd.id)
        if poll is None:
            raise ValueError("User not found")
        await uow.commit()
        return True

async def get_options_for_poll_handler(cmd: commands.GetOptionsForPoll,
                                       uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        poll = await uow.polls.get(cmd.id)
        await uow.commit()
        return poll.options

# Option handlers 

async def create_option_handler(cmd: commands.CreateOption,
                              uow: unit_of_work.AbstractUnitOfWork):
    try: 
        option = models.Option(**asdict(cmd))
    except TypeError:
        raise TypeError("Invalid option data")
    async with uow:
        await uow.options.add(option)
        await uow.commit()
    await redis_eventpublisher.publish(channel="options", event="OptionCreated",
                                       data=asdict(option))
    return True        

async def get_option_handler(cmd: commands.GetOption,
                           uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        option = await uow.options.get(cmd.id)
        await uow.commit()
        return option

async def delete_option_handler(cmd: commands.DeleteOption,
                              uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        option = await uow.options.get(cmd.id)
        if option is None:
            raise ValueError("User not found")
        await uow.commit()
        return True


async def cast_vote(cmd : commands.CastVote, 
                    uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        option = await uow.options.get(cmd.id)
        if option is None:
            raise ValueError("Option not found")
        option.votes += 1
        await uow.commit()
        return True

async def healthcheck_handler(cmd: commands.HealthCheck,
                              uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        await uow.commit()
        return True

EVENT_HANDLERS = {
    events.UserCreated: [create_user_handler],
}

COMMAND_HANDLERS = {
    commands.CreateUser: create_user_handler,
    commands.HealthCheck: healthcheck_handler,
    commands.GetUser: get_user_handler,
    commands.DeleteUser: delete_user_handler,
    commands.CreatePoll: create_poll_handler,
    commands.GetPoll: get_poll_handler,
    commands.DeletePoll: delete_poll_handler,
    commands.GetOptionsForPoll: get_options_for_poll_handler,
    commands.CreateOption: create_option_handler,
    commands.GetOption: get_option_handler,
    commands.DeleteOption: delete_option_handler,
    commands.CastVote: cast_vote
}
