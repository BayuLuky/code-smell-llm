def format_completion(self, item: CompletionItem) -> str:
    return f"{item.type}\n{item.value}\n{item.help if item.help else '_'}"
