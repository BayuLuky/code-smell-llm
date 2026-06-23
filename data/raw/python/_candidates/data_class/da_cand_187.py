class AppConfigStub(AppConfig):
    """Stub of an AppConfig. Only provides a label and a dict of models."""

    def __init__(self, label):
        self.apps = None
        self.models = {}
        # App-label and app-name are not the same thing, so technically passing
        # in the label here is wrong. In practice, migrations don't care about
        # the app name, but we need something unique, and the label works fine.
        self.label = label
        self.name = label

    def import_models(self):
        self.models = self.apps.all_models[self.label]
