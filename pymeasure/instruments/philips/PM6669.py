#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from enum import Enum, IntFlag
from queue import Queue

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class Functions(Enum):
    FREQUENCY_A = 1
    FREQUENCY_B = 2
    RPM_A = 4
    PER_A = 8
    WIDTH_A = 16
    PWIDTH_A = 32
    TOT_A = 64


class HardwareErrorException(Exception):
    pass


class SpollStatus(IntFlag):
    """IntFlag type that represents the status of the device."""

    MEASUREMENT_READY = 1
    READY_FOR_TRIGGERING = 2
    MEASURING_START_ENABLE = 4
    MEASURING_STOP_ENABLE = 8
    GATE_OPEN = 16
    ERROR = 32
    SRQ = 64
    UNUSED2 = 128


class MSRFlag(IntFlag):
    """IntFlag type to build the mask that triggers an service request (SRQ).

    Set this via the MSR command.
    """

    MEASUREMENT_READY = 1
    READY_FOR_TRIGGERING = 2
    MEASURING_START_ENABLE = 4
    MEASURING_STOP_ENABLE = 8
    PROGRAMMING_ERROR = 16
    HARDWARE_FAULT = 32
    TIME_OUT = 64
    UNUSED = 128


class PM6669(Instrument):
    """Represents the Philips PM 6669 instrument."""

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            "Philips PM 6669",
            includeSCPI=False,
            **kwargs
        )
        self.write("EOI ON")
        self.freerun = False
        self.backlog = Queue()

    KEYWORDS = ["FRE", "PER", "WID", "RPM", "PWI"]

    def spoll(self):
        """Read the status of the device."""
        try:
            return SpollStatus(int(self.ask("++spoll")))
        except TypeError:
            return SpollStatus(0)

    def trigger(self):
        """Trigger the device when not in freerun mode."""
        self.write("X")

    def read_measurement(self):
        """Wait for an SRQ from the device and then reads the result.

        Require MSR to be set to MSRFlag.MEASUREMENT_READY
        """
        self.adapter.wait_for_srq(delay=0)
        reply = super().read()
        if reply[:3] in self.KEYWORDS:
            return float(reply.split(" ")[-1])
        else:
            return None

    def ask(self, s):
        """Override ask method to use our own read function."""
        self.write(s)
        return self.read()

    def read(self):
        """Read function with instrument bug work around.

        If a request is made to the device while a measurement is ready, both the reply and the
        measurement are returned. The measurement is filtered out and put in a backlog Queue.
        """
        reply = ''
        result = None
        while reply == '':
            reply = super().read()
            reply = reply.strip('\x00')
            for line in reply.splitlines():
                if line[:3] in self.KEYWORDS:
                    result = line
        return result

    def reset_to_defaults(self):
        """ Resets the instruments to default settings
        """
        self.write("DCL")


PM6669.id = Instrument.measurement(
    "ID?", """ Reads the instrument identification """
)

PM6669.function = Instrument.control(
    "FNC?", "%s", """A string or keyword property that sets measuring function on the device.""",
    validator=strict_discrete_set,
    values={"FREQ A": "FREQ A", "FREQ B": "FREQ B", "RPM A": "RPM A", "PER A": "PER A",
            "WIDTH A": "WIDTH A", "TOTM A": "TOTM A",
            Functions.FREQUENCY_A: "FREQ   A",
            Functions.FREQUENCY_B: "FREQ   B", Functions.PER_A: "PER    A",
            Functions.RPM_A: "RPM    A",
            Functions.WIDTH_A: "PWIDTH A", Functions.TOT_A: "TOTM   A"
            },
    map_values=True
)

PM6669.gate_open = Instrument.measurement(
    "GATE OPEN", """Open the gate and return the current count""",
    get_process=lambda x: float(x[6:])
)

PM6669.gate_close = Instrument.measurement(
    "GATE CLOSE", """Close the gate and return the current count""",
    get_process=lambda x: float(x[6:])
)

PM6669.measurement_time = Instrument.control(
    "MEAC?", "MTIME %g", """ A float property that controls the measurement time""",
    validator=strict_range,
    values=[0, 10],
    get_process=lambda x: float(x[0][5:]) if x[0].startswith("MTIME") is True else 0
)

PM6669.freerun = Instrument.control(
    "MEAC?", "FRUN %s", """ A boolean property that controls the freerun settings""",
    validator=strict_discrete_set,
    values={True: "ON", False: "OFF"},
    map_values=True,
    get_process=lambda x:
    (x[1].split("\n")[0][5:] == " ON") if x[0].startswith("MTIME") is True else 0
)

PM6669.timeout = Instrument.control(
    "MEAC?", "TOUT %s",
    """ A float property that controls the measurement timeout, this timeout only has meaning when
        freerun is off.""",
    validator=strict_range,
    values=[0, 25.5],
    get_process=lambda x: float(x[1].split("\n")[2][5:]) if x[0].startswith("MTIME") is True else 0
)

PM6669.SRQMask = Instrument.control(
    "BUS?", "MSR %i",
    """A integer property that controls the SRQ mask""",
    get_process=lambda x: MSRFlag(int(x[0].split(",")[0].split(" ")[-1]))
)

PM6669.meac = Instrument.measurement(
    "MEAC?", """ Reads the measurement settings from the device """
)
