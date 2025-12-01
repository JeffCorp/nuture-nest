import schedule
from typing import Literal


class ProactiveTools:
    @staticmethod
    def runCronJob(
        value: Literal[
            "seconds", "minutes", "hours", "days", "weeks", "months", "years"
        ],
        label: str,
    ):
        scheduler = schedule.every(value)

        match value:
            case "seconds":
                scheduler.seconds.do(label)
            case "minutes":
                scheduler.minutes.do(label)
            case "hours":
                scheduler.hours.do(label)
            case "days":
                scheduler.days.do(label)
            case "weeks":
                scheduler.weeks.do(label)
            case "months":
                scheduler.months.do(label)
            case "years":
                scheduler.years.do(label)
            case default:
                raise ValueError(f"Invalid value: {value}")
        return scheduler
