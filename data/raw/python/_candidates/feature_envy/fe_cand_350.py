def spider_closed(self, spider):
    task = getattr(self, "task", False)
    if task and task.active():
        task.cancel()

    task_no_item = getattr(self, "task_no_item", False)
    if task_no_item and task_no_item.running:
        task_no_item.stop()
