#
# Copyright (c) 2013, Centre National de la Recherche Scientifique (CNRS)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import logging.handlers
import socket
import time

import stratuslab.controller.util as util


class BaseController():
    def __init__(self, service_name, default_cfg_docid, pause=10):
        """
        The base class for controller daemons.  Subclasses must
        provide the service_name, default_cfg_docid, and an optional
        pause time (in seconds).

        The daemon will read the Couchbase configuration, initial the
        connection to the database, read the service configuration,
        validate the service configuration, then enter the processing
        loop.

        The processing loop will emit a heartbeat message for the
        service, then collect, claim, and process jobs.  This loop is
        repeated until the daemon is stopped.

        The daemon's activity is logged to syslog.  The logger for the
        service has the same name as the service_name.
        """

        self.service_name = service_name
        self.default_cfg_docid = default_cfg_docid
        self.pause = pause
        self.heartbeat_docid = 'Heartbeat/%s/%s' % (self.service_name, socket.getfqdn())

        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/var/run/%s.pid' % self.service_name
        self.pidfile_timeout = 5

    def run(self):

        logger = logging.getLogger(self.service_name)
        logger.setLevel(logging.INFO)

        handler = logging.handlers.SysLogHandler(address='/dev/log')
        formatter = logging.Formatter('%(name)s :: %(levelname)s :: %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        logger.info('starting')

        try:
            cb_cfg = util.read_cb_cfg(self.service_name, self.default_cfg_docid)
            logger.info('read Couchbase configuration: %(host)s, %(bucket)s' % cb_cfg)
        except Exception as e:
            logger.error('error reading Couchbase configuration: %s' % e)
            return 1

        try:
            cb = util.init_cb_client(cb_cfg)
            logger.info('created Couchbase client')
        except Exception as e:
            logger.error('error creating Couchbase client: %s' % e)
            return 1

        try:
            self.cfg = util.get_service_cfg(cb, cb_cfg['cfg_docid'])
            logger.info('read service configuration')
        except Exception as e:
            logger.error('error reading service configuration: %s' % e)
            return 1

        try:
            self._validate_service_cfg()
        except Exception as e:
            logger.error('service configuration error: %s' % e)
            return 1

        logger.info('finished initialization')

        while True:
            util.heartbeat(cb, self.heartbeat_docid)

            for job in self._jobs():
                logger.info('evaluating job %s' % self._job_string(job))
                if self._claim(job):
                    logger.info('claimed job %s' % self._job_string(job))
                    self._execute(job)

            time.sleep(self.pause)

    def _job_string(self, job):
        return job

    def _validate_service_cfg(self):
        """
        This method validates the service configuration read from the
        database.  This method should raise an exception with a
        reasonable message if the service configuration is not valid.
        This default implementation is a no-op.
        """
        pass

    def _jobs(self):
        """
        Used to select jobs from the database.  The method should
        return an array of the selected jobs.  This default
        implementation always returns an empty list.
        """
        return []

    def _claim(self, job):
        """
        Used to evaluate whether a job should be treated by this
        controller or not.  If the job is claimed, then the method
        should update the job with the new status and return True.  It
        should return false otherwise.  Implementations must be aware
        that other controllers may be trying to claim the same job.
        """
        return False

    def _execute(self, job):
        """
        Actually execute the work associated with the given job.  This
        method is responsible for updating the status of the job when
        it has completed.  This implementation is a no-op and does not
        modify the given job.
        """
        pass
