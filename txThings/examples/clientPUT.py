'''
Created on 15-11-2017

@author: Minh Toan
'''

import sys

from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource

from ipaddress import ip_address

coap_server = sys.argv[1]
coap_resoure= sys.argv[2]

class Agent():
    def __init__(self, protocol):
        self.protocol = protocol
        reactor.callLater(1, self.putResource)

    def putResource(self):
        payload = "CoAP Client say hello to server"
        request = coap.Message(code=coap.PUT, payload=payload)
        request.opt.uri_path = (str(coap_resoure),)
        request.opt.content_format = coap.media_types_rev['text/plain']
        request.remote = (coap_server, coap.COAP_PORT)
        d = protocol.request(request)
        d.addCallback(self.printResponse)

    def printResponse(self, response):
        print 'Response Code: ' + coap.responses[response.code]
        print 'Payload: ' + response.payload

log.startLogging(sys.stdout)

endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = Agent(protocol)

reactor.listenUDP(60000, protocol)
reactor.run()
