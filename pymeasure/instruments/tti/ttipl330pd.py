#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from enum import IntFlag
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class LimitEventStatus(IntFlag):
    """ IntFlag type that represents the event status of the device. Used for
        Limit Event Status Register and Limit Event Status Enable Register.
    """
    OUTPUT3_VOLTAGE_LIMIT = 64,
    OUTPUT2_VOLTAGE_LIMIT = 32,
    OUTPUT1_VOLTAGE_LIMIT = 16,
    OUTPUT3_VOLTAGE_TRIP = 8,
    OUTPUT3_CURRENT_LIMIT = 4,
    OUTPUT2_CURRENT_LIMIT = 2,
    OUTPUT1_CURRENT_LIMIT = 1


class StandardEventStatus(IntFlag):
    """ IntFlag that represents the standard status of the device. Used for
        Standard Event Status Register and Standard Event Status Enable Register.
    """
    POWER_ON = 128,
    COMMAND_ERROR = 32,
    EXECUTION_ERROR = 16,
    OPERATION_TIMEOUT_ERROR = 8,
    QUERY_ERROR = 4,
    OPERATION_COMPLETE  = 1


class StatusByte(IntFlag):
    """ IntFlag that represents the status byte of the device. Used by the 
        Status Byte Register and Status Byte Enable Register.
    """
    FAULT_BIT = 128,
    RQS_MSS = 64,
    EVENT_STATUS = 32,
    RESPONSE_READY = 16,
    LIMIT_STATUS = 1


class PL330PD(Instrument):
    """ Represents the TTi PL330PD power supply"""
    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "TTi PL330PD",
            **kwargs
        )
        self.unit = 1
        self.reset

PL330PD.id = Instrument.measurement(
    "*IDN?", """ Reads the instrument identification """
)

PL330PD.voltage = Instrument.control(
    "V1?", "V1 %s",
    """ Controls the set voltage of the power supply in Volts""",
    validator=strict_range,
    values=[0, 32],
    get_process=lambda x:float(x[3:])
)

PL330PD.current = Instrument.control(
    "I1?", "I1 %s",
    """ Controls the set current of the power supply in Volts""",
    get_process=lambda x:float(x[3:])
)

PL330PD.enable = Instrument.control(
    "", "OP1 %s",
    """ Enable the output """,
    validator=strict_discrete_set,
    values=[0 ,1]
)

PL330PD.reset = Instrument.control(
    "*RST", "",
    """ Reset th power supply """
)

PL330PD.clear = Instrument.control(
    "*CLS", "",
    """ Clear status """
)

PL330PD.measured_voltage = Instrument.measurement(
    "V1O?",
    """ Return the measured output voltage """,
    get_process=lambda x:float(x[:-1])
)

PL330PD.measured_current = Instrument.measurement(
    "I1O?",
    """ Return the measured output current """,
    get_process=lambda x:float(x[:-1])
)

PL330PD.standard_event_status_enable_register = Instrument.control(
    "*ESE?", "*ESE %s",
    """ Returns the value in the Standard Event Status Enable Register """,
    get_process=lambda x:StandardEventStatus(int(x[:-1]))
)

PL330PD.standard_event_status_register = Instrument.measurement(
    "*ESR?",
    """ Returns the value in the Standard Event Status Register """,
    get_process=lambda x:StandardEventStatus(int(x[:-1]))
)

PL330PD.service_request_enable_register = Instrument.control(
    "*SRE?", "*SRE %s",
    """ Control the Service Request Enable Register""",
    validator=strict_range,
    values=[0,256],
    get_process=lambda x:StatusByte(int(x[:-1]))
)

PL330PD.limit_event_status_register = Instrument.measurement(
    "LSR?",
    """ Reads and clears the Limit Event Status Register""",
    get_process=lambda x:LimitEventStatus(int(x[:-1]))
)

PL330PD.limit_event_status_enable_register = Instrument.control(
    "LSE?", "LSE %s",
    """ Controls the Limit Event Status Enable Register """,
    get_process=lambda x:LimitEventStatus(int(x[:-1]))
)
