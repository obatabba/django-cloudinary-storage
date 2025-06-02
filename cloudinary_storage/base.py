import os

import cloudinary
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
user_settings = getattr(settings, 'CLOUDINARY_STORAGE', {})

def setting(name, default=None):
    """
    Helper function to get a setting by name. If setting doesn't exists
    it will return a default.

    :param name: Name of setting
    :type name: str
    :param default: Value if setting is unfound
    :returns: Setting's value
    """
    return user_settings.get(name, default)


class BaseStorage(Storage):
    RESOURCE_TYPES = {
        'IMAGE': 'image',
        'RAW': 'raw',
        'VIDEO': 'video'
    }

    def __init__(self, **settings):
        default_settings = self.get_default_settings()

        for name, value in default_settings.items():
            if not hasattr(self, name):
                setattr(self, name, value)

        for name, value in settings.items():
            if name not in default_settings:
                raise ImproperlyConfigured(
                    "Invalid setting '{}' for {}".format(
                        name,
                        self.__class__.__name__,
                    )
                )
            setattr(self, name, value)

        if not self.cloud_name or not self.api_key or not self.api_secret:
            if not os.environ.get('CLOUDINARY_URL'):
                raise ImproperlyConfigured("""
    In order to use cloudinary storage, you need to do ONE of the following:
    
    provide OPTIONS dictionary with cloud_name, api_secret, and api_key in  the settings under STORAGES["default"]
    OR
    provide CLOUDINARY_STORAGE dictionary with CLOUD_NAME, API_SECRET and API_KEY in the settings 
    OR
    set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET environment variables
    OR
    set CLOUDINARY_URL environment variable""")
            return
        else:
            cloudinary.config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret,
                secure=self.secure
            )

    def get_default_settings(self):
        return {
            'cloud_name': setting('CLOUD_NAME', os.environ.get('CLOUDINARY_CLOUD_NAME')),
            'api_key': setting('API_KEY', os.environ.get('CLOUDINARY_API_KEY')),
            'api_secret': setting('API_SECRET', os.environ.get('CLOUDINARY_API_SECRET')),
            'secure': setting('SECURE', True),
            'media_tag': setting('MEDIA_TAG', 'media'),
            'invalid_video_error_message': setting('INVALID_VIDEO_ERROR_NESSAGE', 'Please upload a valid video file.'),
            'exclude_delete_orphaned_media_paths': setting('EXCLUDE_DELETE_ORPHANED_MEDIA_PATHS', ()),
            'static_tag': setting('STATIC_TAG', 'static'),
            'staticfiles_manifest_root': setting('STATICFILES_MANIFEST_ROOT', os.path.join(BASE_DIR, 'manifest')),
            'static_images_extensions': setting('STATIC_IMAGES_EXTENSIONS',
                                [
                                    'jpg',
                                    'jpe',
                                    'jpeg',
                                    'jpc',
                                    'jp2',
                                    'j2k',
                                    'wdp',
                                    'jxr',
                                    'hdp',
                                    'png',
                                    'gif',
                                    'webp',
                                    'bmp',
                                    'tif',
                                    'tiff',
                                    'ico'
                                    ]),
            'static_video_extensions': setting('STATIC_VIDEOS_EXTENSIONS',
                                [
                                    'mp4',
                                    'webm',
                                    'flv',
                                    'mov',
                                    'ogv',
                                    '3gp',
                                    '3g2',
                                    'wmv',
                                    'mpeg',
                                    'flv',
                                    'mkv',
                                    'avi'
                                ]),

            # used only on Windows, see https://github.com/ahupp/python-magic#dependencies for your reference

            'magic_file_path': setting('MAGIC_FILE_PATH', 'magic'),
            'prefix': setting('PREFIX', settings.MEDIA_URL),
        }
