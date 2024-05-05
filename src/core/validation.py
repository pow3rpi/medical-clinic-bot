def check_phone(phone: str) -> bool:
    length: int = len(phone)
    if (
            length not in [10, 11]
            or length == 11 and phone[:2] not in ['79', '89']
            or length == 10 and phone[0] != '9'
    ):
        return False
    else:
        return True


def check_integer(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False
