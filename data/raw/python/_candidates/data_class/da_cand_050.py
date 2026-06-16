class Settings:
    def __init__(self, settings_module):
        # update this dict from global settings (but only for ALL_CAPS settings)
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module

        mod = importlib.import_module(self.SETTINGS_MODULE)

        tuple_settings = (
            "ALLOWED_HOSTS",
            "INSTALLED_APPS",
            "TEMPLATE_DIRS",
            "LOCALE_PATHS",
            "SECRET_KEY_FALLBACKS",
        )
        self._explicit_settings = set()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                if setting in tuple_settings and not isinstance(
                    setting_value, (list, tuple)
                ):
                    raise ImproperlyConfigured(
                        "The %s setting must be a list or a tuple." % setting
                    )
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

        if self.USE_TZ is False and not self.is_overridden("USE_TZ"):
            warnings.warn(
                "The default value of USE_TZ will change from False to True "
                "in Django 5.0. Set USE_TZ to False in your project settings "
                "if you want to keep the current default behavior.",
                category=RemovedInDjango50Warning,
            )

        if self.is_overridden("USE_DEPRECATED_PYTZ"):
            warnings.warn(USE_DEPRECATED_PYTZ_DEPRECATED_MSG, RemovedInDjango50Warning)

        if self.is_overridden("CSRF_COOKIE_MASKED"):
            warnings.warn(CSRF_COOKIE_MASKED_DEPRECATED_MSG, RemovedInDjango50Warning)

        if hasattr(time, "tzset") and self.TIME_ZONE:
            # When we can, attempt to validate the timezone. If we can't find
            # this file, no check happens and it's harmless.
            zoneinfo_root = Path("/usr/share/zoneinfo")
            zone_info_file = zoneinfo_root.joinpath(*self.TIME_ZONE.split("/"))
            if zoneinfo_root.exists() and not zone_info_file.exists():
                raise ValueError("Incorrect timezone setting: %s" % self.TIME_ZONE)
            # Move the time zone info into os.environ. See ticket #2315 for why
            # we don't do this unconditionally (breaks Windows).
            os.environ["TZ"] = self.TIME_ZONE
            time.tzset()

        if self.is_overridden("USE_L10N"):
            warnings.warn(USE_L10N_DEPRECATED_MSG, RemovedInDjango50Warning)

        if self.is_overridden("DEFAULT_FILE_STORAGE"):
            if self.is_overridden("STORAGES"):
                raise ImproperlyConfigured(
                    "DEFAULT_FILE_STORAGE/STORAGES are mutually exclusive."
                )
            self.STORAGES = {
                **self.STORAGES,
                DEFAULT_STORAGE_ALIAS: {"BACKEND": self.DEFAULT_FILE_STORAGE},
            }
            warnings.warn(DEFAULT_FILE_STORAGE_DEPRECATED_MSG, RemovedInDjango51Warning)

        if self.is_overridden("STATICFILES_STORAGE"):
            if self.is_overridden("STORAGES"):
                raise ImproperlyConfigured(
                    "STATICFILES_STORAGE/STORAGES are mutually exclusive."
                )
            self.STORAGES = {
                **self.STORAGES,
                STATICFILES_STORAGE_ALIAS: {"BACKEND": self.STATICFILES_STORAGE},
            }
            warnings.warn(STATICFILES_STORAGE_DEPRECATED_MSG, RemovedInDjango51Warning)
        # RemovedInDjango51Warning.
        if self.is_overridden("STORAGES"):
            setattr(
                self,
                "DEFAULT_FILE_STORAGE",
                self.STORAGES.get(DEFAULT_STORAGE_ALIAS, {}).get("BACKEND"),
            )
            setattr(
                self,
                "STATICFILES_STORAGE",
                self.STORAGES.get(STATICFILES_STORAGE_ALIAS, {}).get("BACKEND"),
            )

    def is_overridden(self, setting):
        return setting in self._explicit_settings

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            "cls": self.__class__.__name__,
            "settings_module": self.SETTINGS_MODULE,
        }
