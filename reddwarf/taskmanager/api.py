# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


"""
Routes all the requests to the task manager.
"""


import logging
import traceback
import sys

from reddwarf.common import config
from reddwarf.common.manager import ManagerAPI


CONFIG = config.Config
LOG = logging.getLogger(__name__)


class API(ManagerAPI):
    """API for interacting with the task manager."""

    def _fake_cast(self, method_name, **kwargs):
        import eventlet
        from reddwarf.taskmanager.manager import TaskManager
        instance = TaskManager()
        method = getattr(instance, method_name)

        def func():
            try:
                method(self.context, **kwargs)
            except Exception as ex:
                type_, value, tb = sys.exc_info()
                logging.error("Error running async task:")
                logging.error((traceback.format_exception(type_, value, tb)))
                raise type_, value, tb

        eventlet.spawn_after(0, func)

    def _get_routing_key(self):
        """Create the routing key for the taskmanager"""
        return CONFIG.get('taskmanager_queue', 'taskmanager')

    def resize_volume(self, new_size, instance_id):
        LOG.debug("Making async call to resize volume for instance: %s"
                 % instance_id)
        self._cast("resize_volume", new_size=new_size, instance_id=instance_id)

    def resize_flavor(self, instance_id, new_flavor_id, old_memory_size,
                      new_memory_size):
        LOG.debug("Making async call to resize flavor for instance: %s" %
                  instance_id)
        self._cast("resize_flavor", instance_id=instance_id,
                   new_flavor_id=new_flavor_id,
                   old_memory_size=old_memory_size,
                   new_memory_size=new_memory_size)

    def reboot(self, instance_id):
        LOG.debug("Making async call to reboot instance: %s" % instance_id)
        self._cast("reboot", instance_id=instance_id)

    def restart(self, instance_id):
        LOG.debug("Making async call to restart instance: %s" % instance_id)
        self._cast("restart", instance_id=instance_id)

    def delete_instance(self, instance_id):
        LOG.debug("Making async call to delete instance: %s" % instance_id)
        self._cast("delete_instance", instance_id=instance_id)

    def create_instance(self, instance_id, name, flavor_id, flavor_ram,
                        image_id, databases, users, service_type, volume_size):
        LOG.debug("Making async call to create instance %s " % instance_id)
        self._cast("create_instance", instance_id=instance_id, name=name,
                   flavor_id=flavor_id, flavor_ram=flavor_ram,
                   image_id=image_id, databases=databases, users=users,
                   service_type=service_type, volume_size=volume_size)
