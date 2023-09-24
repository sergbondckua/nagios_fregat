from aiogram import executor
from aiogram.types import ContentTypes

from apsched.jobs import start_scheduler
from handlers.attach_photo import (
    upload_task_photo,
    start_attach_task_photo,
    cancel_send,
)
from handlers.misc import get_ref, cmd_info_id
from handlers.task_comment import (
    add_task_comment,
    pre_send_comment,
    start_add_task_comment,
    send_comment,
    cancel_comment,
)
from handlers.task_manager import assign_task, send_task
from handlers.users_manager import (
    get_all_users,
    get_simple_user_menu,
    change_user_day_off_duty,
    change_user_staff,
)
from loader import dp, env
from state.attach import AttachFile
from state.comment import AddComment
from utils.db.data_process import DataBaseOperations
from utils.misc import set_locale
from utils.set_bot_commands import set_default_commands

# Import individual handler functions
from handlers import start, helps
from handlers.critical_hosts import (
    send_critical_hosts,
    send_details_critical_hosts,
)
from handlers.credentials import (
    close,
    display_user_profile_menu,
    process_users_query,
    send_balance,
    send_blank,
    send_session,
)
from handlers.usersider import (
    send_access_device,
    show_mac_port,
    telnet_menu,
    cable_test,
    show_errors_port,
)

# Register messages handlers
dp.register_message_handler(start.send_welcome, commands=["start"])
dp.register_message_handler(helps.send_help, commands=["help"])
dp.register_message_handler(send_critical_hosts, commands=["nagios"])
dp.register_message_handler(process_users_query, commands=["abon", "ab"])
dp.register_message_handler(assign_task, commands=["num", "№", "#"])
dp.register_message_handler(assign_task, regexp=r"#\d+")
dp.register_message_handler(get_ref, commands=["ref"])
dp.register_message_handler(cmd_info_id, commands=["myid"])
dp.register_message_handler(get_all_users, commands=["all_users"])
dp.register_message_handler(
    add_task_comment, commands=["add_cmt", "add_comment"]
)
dp.register_message_handler(
    upload_task_photo,
    content_types=ContentTypes.all(),
    state=AttachFile.add_file,
)
dp.register_message_handler(
    pre_send_comment,
    content_types=ContentTypes.TEXT,
    state=AddComment.add_comment,
)

# Register callback handlers
dp.register_callback_query_handler(send_blank, text_contains="blank")
dp.register_callback_query_handler(send_session, text_contains="session")
dp.register_callback_query_handler(send_balance, text_contains="balance")
dp.register_callback_query_handler(send_access_device, text_contains="access")
dp.register_callback_query_handler(telnet_menu, text_contains="telnet")
dp.register_callback_query_handler(show_mac_port, text_contains="show_mac")
dp.register_callback_query_handler(cable_test, text_contains="cable_test")
dp.register_callback_query_handler(send_task, text_contains="send_to")
dp.register_callback_query_handler(
    get_simple_user_menu, text_contains="bot_user"
)
dp.register_callback_query_handler(close, text_contains="close")
dp.register_callback_query_handler(
    change_user_day_off_duty, text_contains="change_duty"
)
dp.register_callback_query_handler(
    change_user_staff, text_contains="change_mounter"
)
dp.register_callback_query_handler(
    cancel_send, text_contains="cancel_send", state="*"
)
dp.register_callback_query_handler(
    cancel_comment, text_contains="cancel_comment", state="*"
)
dp.register_callback_query_handler(
    start_add_task_comment, text_contains="add_comment"
)
dp.register_callback_query_handler(
    send_comment,
    text_contains="approve_send",
    state=AddComment.approve_comment,
)
dp.register_callback_query_handler(
    start_attach_task_photo, text_contains="attach"
)
dp.register_callback_query_handler(
    show_errors_port, text_contains="show_errors"
)
dp.register_callback_query_handler(
    display_user_profile_menu, text_contains="profile"
)
dp.register_callback_query_handler(
    send_details_critical_hosts, text_contains="details"
)


async def on_start(dispatcher) -> None:
    """Start services for bot"""

    # Set commands for bot
    await set_default_commands(dispatcher)

    # Create table if it doesn't exist
    await DataBaseOperations().create_tables()

    # Set locale
    await set_locale(env.str("LOCALE"))

    # Start schedule
    await start_scheduler()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_start)
