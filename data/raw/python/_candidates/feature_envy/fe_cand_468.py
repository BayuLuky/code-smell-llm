def __subclasscheck__(cls, subclass: type) -> bool:
    return (
        hasattr(subclass, "has_pending_requests")
        and callable(subclass.has_pending_requests)
        and hasattr(subclass, "enqueue_request")
        and callable(subclass.enqueue_request)
        and hasattr(subclass, "next_request")
        and callable(subclass.next_request)
    )
