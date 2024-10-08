import traceback


def format_exception(e: Exception) -> str:
    traceback.print_exc()
    msg = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    return msg
