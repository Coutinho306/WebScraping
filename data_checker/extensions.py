import glob
import filecmp

from scrapy import signals
from scrapy.exceptions import NotConfigured


class EmailOnChange(object):
    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool("ENABLE_ON_CHANGE_ENABLED"):
            raise NotConfigured

        # Create and instance of our extension
        extension = cls()

        crawler.signals.connect(extension.engine_stopped, signal=signals.engine_stopped)

        return extension

    def engine_stopped(self):
        print("\n\n\n EXTENSION WAS RUN \n\n\n")
