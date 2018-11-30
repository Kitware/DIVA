from __future__ import absolute_import, unicode_literals
from celery import Celery

app = Celery("dispatcher",
        broker='pyamqp://',
        backend='rpc://',
            include=['tasks'])
app.conf.update(
        CELERYD_MAX_TASKS_PER_CHILD=1
        )

if __name__ == "__main__":
    app.start()
