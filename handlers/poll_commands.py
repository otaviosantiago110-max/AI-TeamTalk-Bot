
import logging

def handle_poll_create(bot, msg_from_id, args_str, **kwargs):
    try:
        parts = [p.strip() for p in args_str.split('"') if p.strip()]
        if len(parts) < 3: raise ValueError(bot.t("poll.usage_create"))

        question, options = parts[0], parts[1:]
        if len(options) > 10: raise ValueError(bot.t("poll.max_options"))

        poll_id = bot.next_poll_id
        bot.next_poll_id += 1
        bot.polls[poll_id] = {'q': question, 'opts': options, 'votes': {}}

        poll_msg = [bot.t("poll.created_header", id=poll_id), bot.t("poll.question_label", question=question)]
        poll_msg.extend(f" {i+1}. {opt}" for i, opt in enumerate(options))
        poll_msg.append(bot.t("poll.vote_instruction", id=poll_id))

        if bot._in_channel:
            bot._send_channel_message(bot._target_channel_id, "\n".join(poll_msg))
            bot._send_pm(msg_from_id, bot.t("poll.created_in_channel", id=poll_id))
        else:
            bot._send_pm(msg_from_id, "\n".join(poll_msg))
    except ValueError as e:
        bot._send_pm(msg_from_id, str(e))
    except Exception as e:
        logging.error(f"Error creating poll: {e}")
        bot._send_pm(msg_from_id, bot.t("poll.create_error"))

def handle_vote(bot, msg_from_id, args_str, **kwargs):
    try:
        poll_id_str, vote_num_str = args_str.split(maxsplit=1)
        poll_id, vote_num = int(poll_id_str), int(vote_num_str)

        if poll_id not in bot.polls: raise ValueError(bot.t("poll.not_found", id=poll_id))
        
        poll_data = bot.polls[poll_id]
        if not (1 <= vote_num <= len(poll_data['opts'])): raise ValueError(bot.t("poll.invalid_option", max=len(poll_data['opts'])))
        
        poll_data['votes'][msg_from_id] = vote_num - 1
        bot._send_pm(msg_from_id, bot.t("poll.vote_recorded", option=poll_data['opts'][vote_num - 1], id=poll_id))
    except (ValueError, IndexError) as e:
        bot._send_pm(msg_from_id, str(e) or bot.t("poll.usage_vote"))

def handle_results(bot, msg_from_id, args_str, **kwargs):
    try:
        poll_id_str = args_str.strip()
        if not poll_id_str:
            active_polls = ', '.join(map(str, bot.polls.keys())) or bot.t("poll.none")
            bot._send_pm(msg_from_id, bot.t("poll.active_polls", list=active_polls)); return

        poll_id = int(poll_id_str)
        if poll_id not in bot.polls: raise ValueError(bot.t("poll.not_found", id=poll_id))

        poll_data = bot.polls[poll_id]
        total_votes = len(poll_data['votes'])
        results = [0] * len(poll_data['opts'])
        for vote_idx in poll_data['votes'].values(): results[vote_idx] += 1

        result_msg = [bot.t("poll.results_header", id=poll_id), bot.t("poll.question_label", question=poll_data['q']), bot.t("poll.total_votes", total=total_votes)]
        for i, opt_text in enumerate(poll_data['opts']):
            count = results[i]
            percent = (count / total_votes * 100) if total_votes > 0 else 0
            result_msg.append(f" {i+1}. {opt_text} - {count} votes ({percent:.1f}%)")
        
        bot._send_pm(msg_from_id, "\n".join(result_msg))
    except ValueError as e:
        bot._send_pm(msg_from_id, str(e) or bot.t("poll.usage_results"))
