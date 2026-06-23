def pre_save(self, model_instance, add):
    file = super().pre_save(model_instance, add)
    if file and not file._committed:
        # Commit the file to storage prior to saving the model
        file.save(file.name, file.file, save=False)
    return file
