# Server Density Elasticsearch plugin
Based on the Server Density Redis plugin

# Installation
Requires the Python Requests library.

Copy Elasticsearch.py to your sd-agent plugins folder, then restart sd-agent.

# Configuration
Takes two optional config parameters:
url: where to find the Elasticsearch HTTP endpoint
node_name: hostname of the Elasticsearch node you want to return statistics about.

Ex section for /etc/sd-agent/config.cfg:
[Elasticsearch]
url: http://127.0.0.1:9200
node_name: elasticsearch01
