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
        reactor.callLater(1, self.requestResource)

    def requestResource(self):
        request = coap.Message(code=coap.GET)
        #Send request to "coap://coap.me:5683/test"
        request.opt.uri_path = (str(coap_resoure),)
        request.opt.observe = 0
        request.remote = (coap_server, coap.COAP_PORT)
        d = protocol.request(request, observeCallback=self.printLaterResponse)
        d.addCallback(self.printResponse)
        # self.printResponse(protocol.response)
        d.addErrback(self.noResponse)

    def printResponse(self, response):
        print ('First result: ' + response.payload)
        #reactor.stop()

    def printLaterResponse(self, response):
        print ('Observe result: ' + response.payload)

    def noResponse(self, failure):
        print ('Failed to fetch resource:')
        print (failure)
        #reactor.stop()

log.startLogging(sys.stdout)

endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = Agent(protocol)

reactor.listenUDP(60000, protocol)
reactor.run()
