import logging


def handle_add_task(bot, msg_from_id, args_str, **kwargs):
    parts = args_str.strip().split()
    if len(parts) != 2 or ':' not in parts[1]:
        bot._send_pm(msg_from_id, bot.t("scheduler.usage_add"))
        return
    action, time_str = parts
    try:
        hour_str, minute_str = time_str.split(':')
        hour, minute = int(hour_str), int(minute_str)
        task_id = bot.task_scheduler.add_task(action, hour, minute)
        bot._send_pm(msg_from_id, bot.t("scheduler.task_added", id=task_id, action=action, time=f"{hour:02d}:{minute:02d}"))
    except ValueError as e:
        bot._send_pm(msg_from_id, str(e))
    except Exception as e:
        logging.error(f"Error adding task: {e}", exc_info=True)
        bot._send_pm(msg_from_id, bot.t("command.unexpected_error", command="addtask", error=e))


def handle_del_task(bot, msg_from_id, args_str, **kwargs):
    arg = args_str.strip()
    if not arg.isdigit():
        bot._send_pm(msg_from_id, bot.t("scheduler.usage_del"))
        return
    if bot.task_scheduler.remove_task(int(arg)):
        bot._send_pm(msg_from_id, bot.t("scheduler.task_removed", id=arg))
    else:
        bot._send_pm(msg_from_id, bot.t("scheduler.task_not_found", id=arg))


def handle_list_tasks(bot, msg_from_id, **kwargs):
    tasks = bot.task_scheduler.list_tasks()
    if not tasks:
        bot._send_pm(msg_from_id, bot.t("scheduler.list_empty"))
        return
    lines = [bot.t("scheduler.list_header")]
    for tid, t in sorted(tasks.items()):
        lines.append(f"  #{tid}: {t['action']} - {t['hour']:02d}:{t['minute']:02d}")
    bot._send_pm(msg_from_id, "\n".join(lines))
