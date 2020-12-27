from crontab import CronTab, CronSlices
from dataclasses import dataclass, field
from collections.abc import Iterable


@dataclass
class Job:
    command: str
    name: str
    frequency: str

@dataclass
class Scheduler:
    jobs: Iterable = field(default_factory=set)
    cron = CronTab(user='root')

    def __validateJob(self):
        for job in self.jobs:
            assert CronSlices.is_valid(job.frequency), job + ": Invalid job frequency."

    def addJob(self, other):
        self.jobs.add(other)

    def clearJob(self, other = None):
        if other:
            self.cron.remove(other)
        else:
            self.cron.remove_all()

    def publish(self):
        self.__validateJob()

        for job in self.jobs:
            new_job = self.cron.new(
                command=job.command,
                comment=job.name,
            )
            new_job.setall(job.frequency)

        self.cron.write()