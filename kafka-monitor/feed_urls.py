#kafka = KafkaMonitor(object)!/usr/bin/python

from __future__ import division
from builtins import str
from builtins import object
from past.utils import old_div
from kafka import KafkaConsumer,KafkaProducer
from kafka.common import KafkaError
from kafka.common import OffsetOutOfRangeError
from collections import OrderedDict
from kafka.common import KafkaUnavailableError
from retrying import retry
import traceback

import time
import json
import sys
import argparse
import redis
import copy
import uuid
import socket
import kafka_monitor

from redis.exceptions import ConnectionError

from jsonschema import ValidationError
from jsonschema import Draft4Validator, validators

from scutils.log_factory import LogFactory
from scutils.settings_wrapper import SettingsWrapper
from scutils.method_timer import MethodTimer
from scutils.stats_collector import StatsCollector
from scutils.argparse_helper import ArgparseHelper

doc = '{"url": "http://facebook.com", "appid":"crawler", "crawlid":"ABC"}'
kafka = kafka_monitor.KafkaMonitor("localsettings.py")#creating an instance
kafka.setup()
with open("top.txt","r+") as f:
    for line in f.readlines():
        data = line
        temp = data.split()
        #print(temp[1])
        json_req  = temp[1]
        try:
            parsed = json.loads(json_req)
        except ValueError:
            kafka.logger.info("JSON failed to parse")
        else:
            print(kafka.feed(parsed))

