from datetime import timedelta


class Duration:
    @classmethod
    def readable(cls, duration: timedelta, use_seconds: bool = False):
        words = []
        years = duration.days // 365
        if years:
            words.append(f"{years} {"year" if years == 1 else "years"}")
        months = (duration.days % 365) // 30
        if months:
            words.append(f"{months} {"month" if months == 1 else "months"}")
        days = ((duration.days % 365) % 30) 
        if days:
            words.append(f"{days} {"day" if days == 1 else "days"}")
        
        hours = duration.seconds // 3600
        if hours:
            words.append(f"{hours} {"hour" if hours == 1 else "hours"}")

        minutes = (duration.seconds % 3600) // 60

        if minutes:
            words.append(f"{minutes} {"minute" if minutes == 1 else "minutes"}")

        if use_seconds:
            seconds = ((duration.seconds % 3600) % 60) 
            if seconds:
                words.append(f"{seconds} {"second" if seconds == 1 else "seconds"}")



        return f"{', '.join(words[:-1])}{' and ' if len(words) > 1 else ''}{words[-1]}" if len(words) else ''
        