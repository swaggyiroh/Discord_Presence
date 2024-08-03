def format_elapsed_time(seconds):
    if seconds is None:
        return "N/A"
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}:{int(minutes):02}:{int(seconds):02}"
