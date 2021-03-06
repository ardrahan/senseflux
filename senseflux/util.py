import datetime


def veghub_time_to_timestamp(created_at: str) -> int:
    parsed = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    zoned = parsed.replace(tzinfo=datetime.timezone.utc)
    return int(zoned.timestamp())
