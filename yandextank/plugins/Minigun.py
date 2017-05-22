from Aggregator import AggregatorPlugin, AggregateResultListener
from yandextank.core import AbstractPlugin
from Phantom import PhantomReader
from ConsoleOnline import ConsoleOnlinePlugin, AbstractInfoWidget
import subprocess
import time
import shlex
import ConsoleScreen
import datetime


class MinigunPlugin(AbstractPlugin, AggregateResultListener):
    SECTION = 'minigun'

    def __init__(self, core):
        AbstractPlugin.__init__(self, core)
        self.process = None
        self.process_stderr = None
        self.process_start_time = None
        self.enum_ammo = False
        self.buffered_seconds = 2

    @staticmethod
    def get_key():
        return __file__

    def get_available_options(self):
        opts = [
            "minigun_cmd",
            "worker_mod",
            "ccw",
            "aps",
            "wps",
            "session_duration",
            "total_duration",
            "auth_url",
            "auth_port",
            "auth_name",
            "auth_pass",
            "api_url",
            "api_port"
        ]
        return opts

    def configure(self):
        ''' Read options from config '''
        self.minigun_cmd = self.get_option("minigun_cmd")
        self.worker_mod = self.get_option("worker_mod")
        self.ccw = self.get_option("ccw")
        self.aps = self.get_option("aps")
        self.wps = self.get_option("wps")
        self.session_duration = self.get_option("session_duration")
        self.total_duration = self.get_option("total_duration")
        self.phout = self.get_option("phout", "")
        self.auth_url = self.get_option("auth_url")
        self.auth_port = self.get_option("auth_port")
        self.auth_name = self.get_option("auth_name")
        self.auth_pass = self.get_option("auth_pass")
        self.api_url = self.get_option("api_url")
        self.api_port = self.get_option("api_port")

        if self.phout:
            self.core.add_artifact_file(self.phout)

    def prepare_test(self):
        aggregator = None
        try:
            aggregator = self.core.get_plugin_of_type(AggregatorPlugin)
        except Exception, ex:
            self.log.warning("No aggregator found: %s", ex)

        if aggregator:
            aggregator.reader = PhantomReader(aggregator, self)
            aggregator.reader.buffered_seconds = self.buffered_seconds
            aggregator.add_result_listener(self)
            aggregator.reader.phout_file = self.phout

        try:
            console = self.core.get_plugin_of_type(ConsoleOnlinePlugin)
        except Exception, ex:
            self.log.debug("Console not found: %s", ex)
            console = None

        if console:
            widget = MinigunInfoWidget(self)
            console.add_info_widget(widget)
            aggregator = self.core.get_plugin_of_type(AggregatorPlugin)
            aggregator.add_result_listener(widget)

    def start_test(self):
        args = [
            self.minigun_cmd,
            self.worker_mod,
            self.ccw,
            self.aps,
            self.wps,
            self.session_duration,
            self.total_duration,
            self.auth_url,
            self.auth_port,
            self.auth_name,
            self.auth_pass,
            self.api_url,
            self.api_port
        ]
        self.log.info("Starting: %s", args)
        self.process_start_time = time.time()
        process_stderr_file = self.core.mkstemp(".log", "minigun_")
        self.core.add_artifact_file(process_stderr_file)
        self.process_stderr = open(process_stderr_file, 'w')
        self.process = subprocess.Popen(
            args,
            stderr=self.process_stderr,
            stdout=self.process_stderr,
            close_fds=True)
        self.process = subprocess.Popen(args, stderr=self.process_stderr, stdout=self.process_stderr, close_fds=True)

    def is_test_finished(self):
        retcode = self.process.poll()
        if retcode is not None:
            self.log.info("Subprocess done its work with exit code: %s", retcode)
            return abs(retcode)
        else:
            return -1

    def end_test(self, retcode):
        if self.process and self.process.poll() is None:
            self.log.warn("Terminating worker process with PID %s", self.process.pid)
            self.process.terminate()
            if self.process_stderr:
                self.process_stderr.close()
        else:
            self.log.debug("Seems subprocess finished OK")
        return retcode

    def get_info(self):
        pass

    def aggregate_second(self, second_aggregate_data):
        pass


class MinigunInfoWidget(AbstractInfoWidget):
    ''' Right panel widget '''
    def __init__(self, uniphout):
        AbstractInfoWidget.__init__(self)
        self.krutilka = ConsoleScreen.krutilka()
        self.owner = uniphout
        self.rps = 0

    def get_index(self):
        return 0

    def aggregate_second(self, second_aggregate_data):
        self.active_threads = second_aggregate_data.overall.active_threads
        self.rps = second_aggregate_data.overall.RPS

    def render(self, screen):
        text = " Uniphout Test %s" % self.krutilka.next()
        space = screen.right_panel_width - len(text) - 1
        left_spaces = space / 2
        right_spaces = space / 2

        dur_seconds = int(time.time()) - int(self.owner.process_start_time)
        duration = str(datetime.timedelta(seconds=dur_seconds))

        template = screen.markup.BG_BROWN + '~' * left_spaces + text + ' ' + '~' * right_spaces + screen.markup.RESET + "\n"
        template += "Command Line: %s\n"
        template += "    Duration: %s\n"
        template += " Responses/s: %s"
        data = (self.owner.minigun_cmd, duration, self.rps)

        return template % data
