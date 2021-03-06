import time
import progressbar
from core import TimeFormat


class STimerOutput:
    def __init__(self, timer, output_fmt=None):
        self.timer = timer
        self.output_fmt = {
            "up": False,
            "sound": True,
            "progress_bar": True,
            "elapsed": True,
            "remaining": True,
        }
        self._init_output_fmt(output_fmt)

    def _init_output_fmt(self, fmt):
        if fmt is None:
            return
        for key in fmt:
            if key in self.output_fmt:
                self.output_fmt[key] = fmt[key]

    def _timer_continue(self):
        if self.output_fmt["up"]:
            if self.timer.duration() is None:
                return True
            elif self.timer.elapsed() < self.timer.duration():
                return True
        else:
            if self.timer.remaining() > 0:
                return True
        return False

    def _get_progress_bar(self):
        wgt_remaining = None
        wgt_elapsed = None
        wgt_bar = None
        bar_max_value = None
        if self.output_fmt["remaining"] is True and self.timer.duration():
            wgt_remaining = progressbar.Variable(name="remaining", format="{value}")
        if self.output_fmt["elapsed"] is True:
            wgt_elapsed = progressbar.Variable(name="elapsed", format="{value}")
        if self.output_fmt["progress_bar"] is True and self.timer.duration():
            wgt_bar = progressbar.Bar(marker="\u2588")
            bar_max_value = self.timer.duration()
        left_text = None
        right_text = None
        if self.output_fmt["up"]:
            left_text = wgt_elapsed
            right_text = wgt_remaining
        else:
            left_text = wgt_remaining
            right_text = wgt_elapsed
        widget_list = [left_text, wgt_bar, right_text]
        widgets = []
        for wgt in widget_list:
            if wgt is not None:
                widgets.append(wgt)
        bar = progressbar.ProgressBar(
            max_value=bar_max_value,
            widgets=widgets,
            variables={
                "remaining": self.timer.remaining(TimeFormat.CLOCK),
                "elapsed": self.timer.elapsed(TimeFormat.CLOCK),
            },
        )
        return bar

    def start_output(self):
        finished = False
        try:
            bar = self._get_progress_bar()
            if self.timer.duration():
                print(
                    "Timer started with duration: "
                    + self.timer.duration(TimeFormat.CLOCK)
                )
            else:
                print("Timer started:")
            while self._timer_continue() is True:
                update_value = None
                if self.output_fmt["progress_bar"] is True:
                    if self.output_fmt["up"]:
                        update_value = self.timer.elapsed()
                    else:
                        update_value = self.timer.remaining()
                else:
                    update_value = 100
                if self.timer.remaining():
                    bar.update(
                        update_value,
                        remaining=self.timer.remaining(TimeFormat.CLOCK),
                        elapsed=self.timer.elapsed(TimeFormat.CLOCK),
                    )
                else:
                    bar.update(
                        update_value, elapsed=self.timer.elapsed(TimeFormat.CLOCK)
                    )
            if self.output_fmt["up"] is True and self.timer.duration():
                update_value = self.timer.duration()
            else:
                update_value = 0
            if self.timer.remaining():
                bar.update(
                    update_value,
                    force=True,
                    remaining=self.timer.remaining(TimeFormat.CLOCK),
                    elapsed=self.timer.elapsed(TimeFormat.CLOCK),
                )
            else:
                bar.update(
                    update_value,
                    force=True,
                    elapsed=self.timer.elapsed(TimeFormat.CLOCK),
                )
            bar.finish(dirty=True)
            finished = True
            if self.output_fmt["sound"] is True:
                print("Time's up! Control + C to exit.", end="", flush=True)
                while True:
                    print("\a", end="", flush=True)
                    time.sleep(0.5)
            else:
                print("Time's up!")
        except KeyboardInterrupt:
            if finished is True:
                print()
        finally:
            if finished is False:
                bar.finish(dirty=True)
