from datetime import datetime, timezone

async def format_timestamp_ms(timestamp_ms):
    timestamp_s = timestamp_ms / 1000
    dt = datetime.fromtimestamp(timestamp_s, timezone.utc)  # UTC час
    return dt.strftime('%Y-%m-%d %H:%M:%S:%f')