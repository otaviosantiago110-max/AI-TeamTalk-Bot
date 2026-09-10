import json
import logging
import threading
from datetime import datetime

# Which notify sound plays for each scheduled action. Assigned in this order
# since the original spec didn't pin specific numbers to specific actions.
TASK_SOUNDS = {
    "maintenance": "notify1.wav",
    "restart": "notify2.wav",
    "shutdown": "notify3.wav",
    "disconnect": "notify4.wav",
}
VALID_ACTIONS = set(TASK_SOUNDS.keys())


class TaskScheduler:
    """Small daily-recurring task scheduler for bot/server maintenance
    actions. Runs in a background thread that only ever *decides* what's
    due; the actual TeamTalk SDK calls happen on the main thread via
    bot._pending_main_thread_actions, same pattern as YouTube playback.

    Tasks are persisted to config.ini (as JSON, under [Bot] scheduled_tasks)
    every time they're added or removed, and reloaded on startup via
    load_from_json() — so they survive a bot restart.
    """

    def __init__(self, bot):
        self.bot = bot
        self._tasks = {}  # id -> {"action", "hour", "minute", "last_run_date"}
        self._next_id = 1
        self._lock = threading.Lock()
        self._stop_flag = threading.Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_flag.set()

    def add_task(self, action, hour, minute):
        action = action.lower().strip()
        if action not in VALID_ACTIONS:
            raise ValueError(self.bot.t("scheduler.invalid_action", actions=', '.join(sorted(VALID_ACTIONS))))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(self.bot.t("scheduler.invalid_time"))
        with self._lock:
            task_id = self._next_id
            self._next_id += 1
            self._tasks[task_id] = {"action": action, "hour": hour, "minute": minute, "last_run_date": None}
        self._persist()
        return task_id

    def remove_task(self, task_id):
        with self._lock:
            removed = self._tasks.pop(task_id, None) is not None
        if removed:
            self._persist()
        return removed

    def list_tasks(self):
        with self._lock:
            return {tid: dict(t) for tid, t in self._tasks.items()}

    def to_json(self):
        """Serializes all tasks (without the id, re-numbered on load) for
        storage in config.ini."""
        with self._lock:
            return json.dumps([
                {"action": t["action"], "hour": t["hour"], "minute": t["minute"]}
                for t in self._tasks.values()
            ])

    def load_from_json(self, json_str):
        """Restores tasks saved by to_json(). Safe to call with '' or invalid
        JSON — just starts with no tasks in that case."""
        try:
            entries = json.loads(json_str) if json_str else []
        except Exception as e:
            logging.warning(f"Scheduler: failed to parse saved tasks, starting empty: {e}")
            entries = []
        with self._lock:
            self._tasks = {}
            self._next_id = 1
            for entry in entries:
                try:
                    action, hour, minute = entry["action"], int(entry["hour"]), int(entry["minute"])
                    if action in VALID_ACTIONS and 0 <= hour <= 23 and 0 <= minute <= 59:
                        self._tasks[self._next_id] = {"action": action, "hour": hour, "minute": minute, "last_run_date": None}
                        self._next_id += 1
                except Exception as e:
                    logging.warning(f"Scheduler: skipping malformed saved task {entry!r}: {e}")

    def _persist(self):
        try:
            self.bot.config.setdefault('Bot', {})['scheduled_tasks'] = self.to_json()
            self.bot._save_runtime_config()
        except Exception as e:
            logging.error(f"Scheduler: failed to persist tasks: {e}", exc_info=True)

    def _run(self):
        while not self._stop_flag.is_set():
            now = datetime.now()
            due = []
            with self._lock:
                for tid, t in self._tasks.items():
                    if t["hour"] == now.hour and t["minute"] == now.minute and t["last_run_date"] != now.date():
                        t["last_run_date"] = now.date()
                        due.append(t["action"])
            for action in due:
                self._fire(action)
            self._stop_flag.wait(20)  # 20s resolution is plenty for a minute-granularity scheduler

    def _fire(self, action):
        def _on_main_thread(bot):
            sound = TASK_SOUNDS.get(action, "notify1.wav")
            bot._play_channel_sound(sound)
            announcement = bot.t("scheduler.announce", action=action)
            try:
                channel_id = bot.getMyChannelID()
                if channel_id:
                    bot._send_channel_message(channel_id, announcement)
            except Exception as e:
                logging.warning(f"Scheduler: failed to announce task '{action}' in channel: {e}")
            try:
                bot._send_broadcast(announcement)
            except Exception as e:
                logging.warning(f"Scheduler: failed to broadcast task '{action}': {e}")

            if action == "restart":
                bot._initiate_restart()
            elif action == "shutdown":
                bot._running = False
            elif action == "disconnect":
                try:
                    bot.disconnect()
                except Exception as e:
                    logging.warning(f"Scheduler: failed to disconnect: {e}")
            # "maintenance" is just a notification for now — no automatic action.

        self.bot._pending_main_thread_actions.put(_on_main_thread)
