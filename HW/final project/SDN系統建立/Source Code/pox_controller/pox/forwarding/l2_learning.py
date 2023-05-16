

# The following comments are my referenced code,
# and i made it to realize and code them again.

"""
# Copyright 2011-2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

An L2 learning switch.

It is derived from one written live for an SDN crash course.
It is somwhat similar to NOX's pyswitch in that it installs
exact-match rules for each flow.
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str, str_to_dpid
from pox.lib.util import str_to_bool
import time

# We don't want to flood immediately when a switch connects.
# Can be overriden on commandline.
_flood_delay = 0


class LearningSwitch (object):
    """
    The detail can access in the report, the main function of the class is to make 
    controller learn port table, and help OVS forward the unknown packet.
    """
    def __init__(self, connection, transparent):
        # Switch we'll be adding L2 learning switch capabilities to
        self.listener = connection
        self.transparent = transparent

        # Port table
        self.portTable = {}

        # The Listener to stand by for PacketIn packets
        connection.addListeners(self)
        self.hold_down_expired = _flood_delay == 0

    def _handle_PacketIn(self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """

        packet = event.parsed

        def flood(message=None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            if time.time() - self.listener.connect_time >= _flood_delay:
                # OFPP_FLOOD is optional; on some switches you may need to change
                # this to OFPP_ALL.
                msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            else:
                pass
            msg.data = event.ofp
            msg.in_port = event.port
            self.listener.send(msg)

        def drop(duration=None):
            """
            Drops this packet and optionally installs a flow to continue
            dropping similar ones for a while
            """
            if duration is not None:
                if not isinstance(duration, tuple):
                    duration = (duration, duration)
                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match.from_packet(packet)
                msg.idle_timeout = duration[0]
                msg.hard_timeout = duration[1]
                msg.buffer_id = event.ofp.buffer_id
                self.listener.send(msg)
            elif event.ofp.buffer_id is not None:
                msg = of.ofp_packet_out()
                msg.buffer_id = event.ofp.buffer_id
                msg.in_port = event.port
                self.listener.send(msg)

        # It's gonna store the packet Info into my port table.
        self.portTable[packet.src] = event.port  # 1

        # Any packet belonging to transparent, member of black list, LLDP will be dropped.
        if not self.transparent:
            if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
                drop()
                return

        # Flood it with multicast flag, or it's gonna forward to the specific port.
        if packet.dst.is_multicast:
            flood()
        else:
            # If the packet Info hasn't in the port table, flood it.
            # else forward to the recorded port.
            if packet.dst not in self.portTable:
                flood("Port for %s unknown -- flooding" % (packet.dst,))
            else:
                port = self.portTable[packet.dst]
                # Drop the packet which its input port is output port 
                # to avoid infinite forwarding.
                if port == event.port:
                    drop(10)
                    return
                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match.from_packet(packet, event.port)
                msg.idle_timeout = 10
                msg.hard_timeout = 30
                msg.actions.append(of.ofp_action_output(port=port))
                msg.data = event.ofp
                self.listener.send(msg)


class l2_learning (object):
    """
    When controller is prepared, it will connect OVS and make them learn port table.
    """

    def __init__(self, transparent, ignore=None):
        core.openflow.addListeners(self)
        self.transparent = transparent
        self.ignore = set(ignore) if ignore else ()

    def _handle_ConnectionUp(self, event):
        if event.dpid in self.ignore:
            return
        LearningSwitch(event.connection, self.transparent)


def launch(transparent=False, hold_down=_flood_delay, ignore=None):
    """
    Start an L2 learning switch.
    """
    try:
        global _flood_delay
        _flood_delay = int(str(hold_down), 10)
        assert _flood_delay >= 0
    except:
        raise RuntimeError("Expected hold-down to be a number")

    if ignore:
        ignore = ignore.replace(',', ' ').split()
        ignore = set(str_to_dpid(dpid) for dpid in ignore)

    core.registerNew(l2_learning, str_to_bool(transparent), ignore)
