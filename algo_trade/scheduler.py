from crontab import CronTab, CronSlices
from dataclasses import dataclass, field
from collections.abc import Iterable

import os


@dataclass(frozen=True)
class Job:
    command: str
    name: str
    frequency: str
    output: str = None

@dataclass
class Scheduler:
    jobs: Iterable = field(default_factory=set)
    cron = CronTab(user=True)

    def __validateJob(self, job):
        assert job.is_valid(), "Invalid job frequency."

    def addJob(self, other):
        self.jobs.add(other)

    def clearJob(self, **kwargs):
        if kwargs:
            self.cron.remove_all(**kwargs)
        else:
            self.cron.remove_all()

    def findJob(self, path):
        exclude_regex = {'.', '_'}

        for filename in os.listdir(path):
            if filename[0] not in exclude_regex:
                command = os.path.join(path, filename)
                print(command)

                self.jobs.add(Job(
                    command=command,
                    name=filename.split('.')[0],
                    frequency='59 23 1-7,15-21 * 0', # At 23:59 on every day-of-month from 1 through 7 and every day-of-month from 15 through 21 and on Sunday.
                ))

    def listJob(self):
        for item in self.cron:
            print(item)

    def publish(self):

        for job in self.jobs:
            new_job = self.cron.new(
                command=job.command,
                comment=job.name,
            )
            new_job.setall(job.frequency)
            self.__validateJob(new_job)

        self.cron.write()

if __name__ == '__main__':
    scheduler = Scheduler()
    path = '/Users/vtamprateep/Documents/algo-portfolio/algo_trade'
    #scheduler.findJob(path)
    scheduler.listJob()
    scheduler.clearJob()
    scheduler.publish()