"""
Bridge class that allows PyXLL to display plotly dash apps
by serving them in a background thread.
"""
from pyxll import PlotBridgeBase, xl_plot_bridge
import concurrent.futures
import threading
import logging

_log = logging.getLogger(__name__)

_timeout = 15

_template = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url='{url}'" />
</head>
<body>
    <p>If you are not redirected automatically, follow this <a href="{url}">link to {url}</a>.</p>
</body>
</html>
"""

class DashServerThread:

    def __init__(self, app):
        self.app = app
        self.server = None
        self.thread = None
        self.stopped_event = threading.Event()

    def __thread_func(self, future, **kwargs):
        try:
            # Import this here so as not to slow down Excel's loading
            from werkzeug.serving import make_server

            assert self.server is None
            self.server = make_server('127.0.0.1', 0, self.app.server)
            self.ctx = self.app.server.app_context()
            self.ctx.push()
            future.set_result(self.server)
            self.server.serve_forever()
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            self.stopped_event.set()

    def start(self, **kwargs):
        assert self.thread is None

        future = concurrent.futures.Future()

        _log.debug("Dash server starting")
        self.thread = threading.Thread(
            target=self.__thread_func,
            args=(future,),
            kwargs=kwargs
        )

        self.thread.daemon = True
        self.thread.start()

        try:
            # Wait for the server to finish starting up and return it
            return future.result(timeout=_timeout)
        except:
            # Stop the server if there was an error
            self.stop()
            raise

    def stop(self):
        self.server.shutdown()
        self.stopped_event.wait(timeout=_timeout)
        _log.debug("Dash server shutdown")


@xl_plot_bridge("dash.dash.Dash")
class DashBridge(PlotBridgeBase):

    def __init__(self, app):
        PlotBridgeBase.__init__(self, app)
        self.app = app

    def can_export(self, format):
        return format == "html"

    def export(self, width, height, dpi, format, filename, **kwargs):
        if format != "html":
            raise ValueError("Unable to export as '%s'" % str(format))

        thread = DashServerThread(self.app)
        server = thread.start(**kwargs)

        try:
            # Write some html to redirect to our newly started server
            host = server.host or 'localhost'
            url = f"http://{host}:{server.port}/"

            with open(filename, "wt") as fh:
                fh.write(_template.format(url=url))

        except:
            # Stop the thread if there was an error
            thread.stop()
            raise

        # This will be called when the control hosting the page is destroyed
        return thread.stop
