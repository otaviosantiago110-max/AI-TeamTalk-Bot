
import logging
import i18n

def handle_set_language(bot, msg_from_id, args_str, **kwargs):
    lang = i18n.normalize_language(args_str.strip())
    bot.language = lang
    bot._save_runtime_config()
    bot._send_pm(msg_from_id, bot.t("language.set_confirmation", new_lang=lang))

def handle_set_gapi(bot, msg_from_id, args_str, **kwargs):
    if not args_str:
        bot._send_pm(msg_from_id, bot.t("config.usage_gapi")); return

    new_api_key = args_str.strip()
    original_api_key = bot.groq_service.api_key # Store original key

    # Temporarily set and try to initialize with the new key
    bot.groq_service.api_key = new_api_key
    bot.groq_service.init_model()

    if bot.groq_service.is_enabled():
        bot.allow_groq_pm = True
        bot.allow_groq_channel = True
        feedback = bot.t("config.gapi_success")
        bot._save_runtime_config(save_groq_key=True)
    else:
        # If initialization failed, revert to original key and disable Groq features
        bot.groq_service.api_key = original_api_key # Revert API key
        bot.groq_service.init_model() # Re-initialize with original key
        bot.allow_groq_pm = False
        bot.allow_groq_channel = False
        feedback = bot.t("config.gapi_failed")
    
    bot._send_pm(msg_from_id, feedback)
    if bot.main_window: bot.main_window.update_feature_list()

def handle_list_groq_models(bot, msg_from_id, **kwargs):
    if not bot.groq_service.is_enabled():
        bot._send_pm(msg_from_id, bot.t("config.groq_disabled_list")); return
    
    models = bot.groq_service.list_available_models()
    if models:
        model_list_str = bot.t("config.groq_models_header", list="\n".join(models))
        bot._send_pm(msg_from_id, model_list_str)
    else:
        bot._send_pm(msg_from_id, bot.t("config.groq_models_none"))

def handle_set_groq_model(bot, msg_from_id, args_str, **kwargs):
    if not args_str:
        bot._send_pm(msg_from_id, bot.t("config.usage_set_groq_model")); return
    
    new_model_name = args_str.strip()
    if bot.set_groq_model(new_model_name):
        bot._send_pm(msg_from_id, bot.t("config.set_groq_model_success", model=new_model_name))
    else:
        bot._send_pm(msg_from_id, bot.t("config.set_groq_model_failed", model=new_model_name))

def handle_set_context_retention(bot, msg_from_id, args_str, **kwargs):
    try:
        retention_minutes = int(args_str.strip())
        if retention_minutes < 0:
            raise ValueError(bot.t("config.retention_negative"))
        
        bot.context_history_manager.set_retention_minutes(retention_minutes)
        bot.config['Bot']['context_history_retention_minutes'] = str(retention_minutes)
        bot._save_runtime_config()
        bot._send_pm(msg_from_id, bot.t("config.retention_set", minutes=retention_minutes))
    except ValueError:
        bot._send_pm(msg_from_id, bot.t("config.usage_retention"))
    except Exception as e:
        logging.error(f"Error setting context retention: {e}")
        bot._send_pm(msg_from_id, bot.t("config.retention_error", error=e))

def handle_add_word(bot, msg_from_id, args_str, **kwargs):
    word = args_str.strip().lower()
    if not word:
        bot._send_pm(msg_from_id, bot.t("config.usage_addword")); return
    bot.filtered_words.add(word)
    bot.filter_enabled = True
    bot._save_runtime_config()
    bot._send_pm(msg_from_id, bot.t("config.word_added", word=word))

def handle_del_word(bot, msg_from_id, args_str, **kwargs):
    word = args_str.strip().lower()
    if not word:
        bot._send_pm(msg_from_id, bot.t("config.usage_delword")); return
    bot.filtered_words.discard(word)
    if not bot.filtered_words:
        bot.filter_enabled = False
    bot._save_runtime_config()
    bot._send_pm(msg_from_id, bot.t("config.word_removed", word=word))

def handle_set_ai_system_instructions(bot, msg_from_id, args_str, **kwargs):
    if not args_str:
        bot._send_pm(msg_from_id, bot.t("config.usage_instructions")); return
    instructions = args_str.strip()
    if bot.set_ai_system_instructions(instructions):
        bot._send_pm(msg_from_id, bot.t("config.instructions_updated"))
    else:
        bot._send_pm(msg_from_id, bot.t("config.instructions_failed"))

def handle_set_welcome_instruction(bot, msg_from_id, args_str, **kwargs):
    if not args_str:
        bot._send_pm(msg_from_id, bot.t("config.usage_welcome_instructions")); return
    instructions = args_str.strip()
    if bot.set_welcome_message_instructions(instructions):
        bot._send_pm(msg_from_id, bot.t("config.welcome_instructions_updated"))
    else:
        bot._send_pm(msg_from_id, bot.t("config.welcome_instructions_failed"))

