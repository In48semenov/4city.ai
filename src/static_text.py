HELLO_TEXT = "Привет, %s! Я бот, который помогает делать красивые вывески. Пришли мне фото с вывеской и я постараюсь " \
             "сделать ее красивой."
NON_TARGET_TEXT = "\U0001f972 Прости, %s, я могу работать только с фото"
WAITING_TEXT = "%s, скоро мы обработаем твою фотографию"
NON_TARGET_CONTENT_TYPES = [
    'audio', 'document', 'sticker', 'video', 'video_note', 'voice',
    'location',
    'contact', 'new_chat_members', 'left_chat_member', 'new_chat_title',
    'new_chat_photo',
    'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created',
    'channel_chat_created',
    'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message'
]
NON_LABELS_TEXT = "\U0001f972 Кажется, на фотографии вывесок. Попробуй другое фото."