"""
  Server Density Plugin
  Elasticsearch Node Statistics

  https://github.com/larsla/serverdensity-elasticsearch
  Based on the Server Density Redis plugin

  Version: 0.1.0

  Takes two optional config parameters:
  url: where to find the Elasticsearch HTTP endpoint
  node_name: hostname of the Elasticsearch node you want to return statistics about.
"""

import json
import logging
import os
import platform
import sys
import time
import socket
import collections


class Elasticsearch(object):

    def __init__(self, agent_config, checks_logger, raw_config):
        self.agent_config = agent_config
        self.checks_logger = checks_logger
        self.raw_config = raw_config
        self.version = platform.python_version_tuple()
        try:
            import requests
        except Exception:
            self.checks_logger.error(
                'Python Requests module not installed,' +
                'please install https://pypi.python.org/pypi/requests/')

        self.url = self.raw_config['Elasticsearch'].get('url', 'http://localhost:9200')
        self.node_name = self.raw_config['Elasticsearch'].get('node_name', socket.gethostname())

    def run(self):
        import requests
        data = {}
        stats = None

        # Get cluster statistics
        try:
            r = requests.get('%s/_cluster/stats' % self.url)
            data.update(self._flatten(json.loads(r.text), parent_key='cluster'))
        except Exception, e:
            self.checks_logger.exception("Caught exception: %s" % e)

        # Get node statistics
        try:
            r = requests.get('%s/_nodes/%s/stats' % (self.url, self.node_name))
            d = json.loads(r.text)
            if not 'nodes' in d:
                self.checks_logger.error("No nodes listed in statistics endpoint")
                return {}

            for node in d['nodes'].keys():
                if d['nodes'][node]['host'] == self.node_name:
                    data.update(self._flatten(d['nodes'][node], parent_key='node'))
                    break
        except Exception, e:
            self.checks_logger.exception("Caught exception: %s" % e)

        return data


    def _flatten(self, d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(self._flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


if __name__ == '__main__':
    """Standalone test
    """

    raw_agent_config = {
        'Elasticsearch': {
            'url': 'http://elk-intprod-rslon-elastic01.int.leovegas.net:9200',
            'node_name': 'elk-intprod-rslon-elastic01',
        }
    }

    main_checks_logger = logging.getLogger('Elasticsearch')
    main_checks_logger.setLevel(logging.DEBUG)
    main_checks_logger.addHandler(logging.StreamHandler(sys.stdout))
    elasticsearch_check = Elasticsearch({}, main_checks_logger, raw_agent_config)

    while True:
        try:
            print json.dumps(elasticsearch_check.run(), indent=4, sort_keys=True)
        except:
            main_checks_logger.exception("Unhandled exception")
        finally:
            time.sleep(60)
