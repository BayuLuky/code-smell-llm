def format_completion(self, item: CompletionItem) -> str:
    if item.help:
        return f"{item.type},{item.value}\t{item.help}"

    return f"{item.type},{item.value}"
