from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string


class ImportDict(dict):
    def __getattribute__(self, item):
        """Whenever accessing an attribute, attempt to import it and override the
        underlying dictionary str value with this import."""
        val = self[item]
        if isinstance(val, str):
            val = import_string(val)
        self[item] = val
        return val


chat_settings = {
    'SERIALIZERS': ImportDict({
        # NOTE: these are referenced like chat_settings.USER (as attribute, not dict key!)
        'USER': 'chit_chat.serializers.ChatUserSerializer',
        'MESSAGE': 'chit_chat.consumer_serializers.ChatMessageSerializer',
    })
}


def load_or_reload_settings(setting=None, **kwargs):
    if setting is not None and setting != 'CKC_CHAT_SERIALIZERS':
        return
    # Override default serializers..
    if hasattr(settings, 'CKC_CHAT_SERIALIZERS'):
        for name, module in settings.CKC_CHAT_SERIALIZERS.items():
            chat_settings['SERIALIZERS'][name] = module


load_or_reload_settings()

setting_changed.connect(load_or_reload_settings)
