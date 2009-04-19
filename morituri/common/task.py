# -*- Mode: Python; test-case-name: morituri.test.test_common_task -*-
# vi:si:et:sw=4:sts=4:ts=4

# Morituri - for those about to RIP

# Copyright (C) 2009 Thomas Vander Stichele

# This file is part of morituri.
# 
# morituri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# morituri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with morituri.  If not, see <http://www.gnu.org/licenses/>.

import sys

import gobject
import gtk

class Task(object):
    """
    I wrap a task in an asynchronous interface.
    I can be listened to for starting, stopping, and progress updates.

    @ivar  description: what am I doing
    """
    description = 'I am doing something.'

    progress = 0.0
    increment = 0.01
    running = False
    runner = None

    _listeners = None


    ### subclass methods
    def start(self, runner):
        """
        Start the task.

        Subclasses should chain up to me at the beginning.
        """
        self.progress = 0.0
        self.running = True
        self.runner = runner
        self._notifyListeners('started')

    def stop(self):
        """
        Stop the task.

        Subclasses should chain up to me at the end.
        """
        self.debug('stopping')
        self.running = False
        self.runner = None
        self._notifyListeners('stopped')

    ### base class methods
    def debug(self, *args, **kwargs):
        return
        print self, args, kwargs
        sys.stdout.flush()

    def setProgress(self, value):
        """
        Notify about progress changes bigger than the increment.
        Called by subclass implementations as the task progresses.
        """
        if value - self.progress > self.increment or value >= 1.0 or value == 0.0:
            self.progress = value
            self._notifyListeners('progressed', value)
            self.debug('notifying progress', value)
        
    def addListener(self, listener):
        """
        Add a listener for task status changes.

        Listeners should implement started, stopped, and progressed.
        """
        if not self._listeners:
            self._listeners = []
        self._listeners.append(listener)

    def _notifyListeners(self, methodName, *args, **kwargs):
            if self._listeners:
                for l in self._listeners:
                    getattr(l, methodName)(self, *args, **kwargs)

# this is a Dummy task that can be used if this works at all
class DummyTask(Task):
    def start(self, runner):
        Task.start(self, runner)
        self.runner.schedule(1.0, self._wind)

    def _wind(self):
        self.setProgress(min(self.progress + 0.1, 1.0))

        if self.progress >= 1.0:
            self.stop()
            return

        self.runner.schedule(1.0, self._wind)


class TaskRunner:
    """
    I am a base class for task runners.
    Task runners should be reusable.
    """

    def run(self, task):
        """
        Run the given task.

        @type  task: Task
        """
        raise NotImplementedError

    ### methods for tasks to call
    def schedule(self, delta, callable, *args, **kwargs):
        """
        Schedule a single future call.

        Subclasses should implement this.

        @type  delta: float
        @param delta: time in the future to schedule call for, in seconds.
        """
        raise NotImplementedError

    ### listener callbacks
    def progressed(self, task, value):
        """
        Implement me to be informed about progress.

        @type  value: float
        @param value: progress, from 0.0 to 1.0
        """

    def started(self, task):
        """
        Implement me to be informed about the task starting.
        """

    def stopped(self, task):
        """
        Implement me to be informed about the task starting.
        """


class SyncRunner(TaskRunner):
    """
    I run the task synchronously in a gobject MainLoop.
    """
    def run(self, task, verbose=True, skip=False):
        self._task = task
        self._verbose = verbose
        self._skip = skip

        self._loop = gobject.MainLoop()
        self._task.addListener(self)
        # only start the task after going into the mainloop,
        # otherwise the task might complete before we are in it
        gobject.timeout_add(0L, self._task.start, self)
        self._loop.run()

    def schedule(self, delta, callable, *args, **kwargs):
        def c():
            callable(*args, **kwargs)
            return False
        gobject.timeout_add(int(delta * 1000L), c)

    def progressed(self, task, value):
        if not self._verbose:
            return

        sys.stdout.write('%s %3d %%\r' % (
            self._task.description, value * 100.0))
        sys.stdout.flush()

        if value >= 1.0:
            if self._skip:
                sys.stdout.write('%s %3d %%\n' % (
                    self._task.description, 100.0))
            else:
                # clear with whitespace
                text = '%s %3d %%' % (
                    self._task.description, 100.0)
                sys.stdout.write("%s\r" % (' ' * len(text), ))

    def stopped(self, task):
        self._loop.quit()


class GtkProgressRunner(gtk.VBox, TaskRunner):
    """
    I am a widget that shows progress on a task.
    """

    __gsignals__ = {
        'stop': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
    }

    def __init__(self):
        gtk.VBox.__init__(self)
        self.set_border_width(6)
        self.set_spacing(6)

        self._label = gtk.Label()
        self.add(self._label)

        self._progress = gtk.ProgressBar()
        self.add(self._progress)

    def run(self, task):
        self._task = task
        self._label.set_text(task.description)
        task.addListener(self)
        while gtk.events_pending():
            gtk.main_iteration()
        task.start(self)

    def schedule(self, delta, callable, *args, **kwargs):
        def c():
            callable(*args, **kwargs)
            return False
        gobject.timeout_add(int(delta * 1000L), c)

    def started(self, task):
        pass

    def stopped(self, task):
        self.emit('stop')
        # self._task.removeListener(self)

    def progressed(self, task, value):
        self._label.set_text(task.description)
        self._progress.set_fraction(value)


if __name__ == '__main__':
    task = DummyTask()
    runner = SyncRunner()
    runner.run(task)