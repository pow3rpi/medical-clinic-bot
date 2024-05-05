from aiogram import Dispatcher

from src.handlers import commands
from src.handlers.admin import (
    admin_panel_nav, create_doctor, update_doctor, delete_doctor,
    show_doctor, statistic, create_admin, delete_admin
)
from src.handlers.client import (
    callback, appointment, feedback,
    contacts, instruction
)


def register_handlers(dp: Dispatcher) -> None:
    # register commands
    commands.register_handlers(dp)

    # register admin handlers
    admin_panel_nav.register_handlers(dp)
    create_doctor.register_handlers(dp)
    update_doctor.register_handlers(dp)
    delete_doctor.register_handlers(dp)
    show_doctor.register_handlers(dp)
    statistic.register_handlers(dp)
    create_admin.register_handlers(dp)
    delete_admin.register_handlers(dp)

    # register client handlers
    callback.register_handlers(dp)
    appointment.register_handlers(dp)
    feedback.register_handlers(dp)
    contacts.register_handlers(dp)
    instruction.register_handlers(dp)

    return
