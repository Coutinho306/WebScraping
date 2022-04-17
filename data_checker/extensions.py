import glob
import filecmp

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.mail import MailSender


class EmailOnChange(object):
    def __init__(self, destination, mailer):
        self.destination = destination
        self.mailer = mailer

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool("ENABLE_ON_CHANGE_ENABLED"):
            raise NotConfigured

        destination = crawler.settings.get("ENABLE_ON_CHANGE_DESTINATION")
        if not destination:
            raise NotConfigured("ENABLE_ON_CHANGE_DESTINATION must be provided")

        mailer = MailSender.from_settings(crawler.settings)

        # Create and instance of our extension
        extension = cls(destination, mailer)

        crawler.signals.connect(extension.engine_stopped, signal=signals.engine_stopped)

        return extension

    def engine_stopped(self):
        # list Out previous runs
        runs = sorted(
            glob.glob("/tmp/[0-9]*-[0-9]*-[0-9]*T[0-9]*-[0-9]*-[0-9]*.json"),
            reverse=True,
        )

        if len(runs) < 2:
            # We can't compare if there's only 1 run
            return

        # Grab the newest 2 runs
        current_file, previous_file = runs[0:2]

        # Compare then
        # If difference in the output, then send an email
        if not filecmp.cmp(current_file, previous_file):
            print("\n\n THE FILES ARE DIFFERENT \n\n")
            with open(current_file) as f:
                self.mailer.send(
                    to=[self.destination],
                    subject="Datasets Changed!",
                    body="Changes in datasets detected, see attachment for current datasets",
                    attachs=[(current_file.split("/")[-1], "application/json", f)],
                )
        else:
            print("\n\n NO CHANGE \n\n")
