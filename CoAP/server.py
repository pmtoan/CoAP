'''
Created on 20-11-2017

@author: Minh Toan
'''

import sys
import datetime
import trigger
from twisted.internet import defer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.resource as resource
import txthings.coap as coap


class CounterResource (resource.CoAPResource):
    def __init__(self, start=0):
        resource.CoAPResource.__init__(self)
        self.counter = start
        self.visible = True
        self.addParam(resource.LinkParam("title", "Counter resource"))

    def render_GET(self, request):
        response = coap.Message(code=coap.CONTENT, payload='%d' % (self.counter,))
        self.counter += 1
        return defer.succeed(response)


class BlockResource (resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True

    def render_GET(self, request):
        payload="CoAP server hello to client"
        response = coap.Message(code=coap.CONTENT, payload=payload)
        return defer.succeed(response)

    def render_PUT(self, request):
        print 'PUT payload: ' + request.payload
        payload = "CoAP server hello to client"
        response = coap.Message(code=coap.CHANGED, payload=payload)
        return defer.succeed(response)


class SeparateLargeResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.addParam(resource.LinkParam("title", "Large resource."))

    def render_GET(self, request):
        d = defer.Deferred()
        reactor.callLater(3, self.responseReady, d, request)
        return d

    def responseReady(self, d, request):
        log.msg('response ready. sending...')
        payload = "Three rings for the elven kings under the sky, seven rings for dwarven lords in their halls of stone, nine rings for mortal men doomed to die, one ring for the dark lord on his dark throne."
        response = coap.Message(code=coap.CONTENT, payload=payload)
        d.callback(response)

class TimeResource(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.visible = True
        self.observable = True

        self.notify()

    def notify(self):
        log.msg('TimeResource: trying to send notifications')
        self.updatedState()
        reactor.callLater(60, self.notify)

    def render_GET(self, request):
        response = coap.Message(code=coap.CONTENT, payload=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        return defer.succeed(response)

class CoreResource(resource.CoAPResource):
    def __init__(self, root):
        resource.CoAPResource.__init__(self)
        self.root = root

    def render_GET(self, request):
        data = []
        self.root.generateResourceList(data, "")
        payload = ",".join(data)
        print payload
        response = coap.Message(code=coap.CONTENT, payload=payload)
        response.opt.content_format = coap.media_types_rev['application/link-format']
        return defer.succeed(response)

class TempResources(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        self.temp = trigger.probe_temp()
	self.payl = str(self.temp) + "*C"
        self.visible = True
        self.addParam(resource.LinkParam("title", "Temp resource"))

    def render_GET(self, request):
        response = coap.Message(code=coap.CONTENT, payload='%s' % (self.payl,))
        return defer.succeed(response)

class CPUResources(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        line = "Arch: armv6l"
        line += " CPUs: 1"
        line += " Speed: 700 MHz"
        self.mess = line
        self.visible = True
        self.addParam(resource.LinkParam("title", "CPU resource"))

    def render_GET(self, request):
        response = coap.Message(code=coap.CONTENT, payload='%s' % (self.mess,))
        return defer.succeed(response)

class DiskResources(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        line = "Mem: 434M Swap: 99M Dev: 7G"
        self.mess = line
        self.visible = True
        self.addParam(resource.LinkParam("title", "Disk resource"))

    def render_GET(self, request):
        response = coap.Message(code=coap.CONTENT, payload='%s' % (self.mess,))
        return defer.succeed(response)

class OSResources(resource.CoAPResource):
    def __init__(self):
        resource.CoAPResource.__init__(self)
        line = "Linux raspbian 4.9.41+"
        self.mess = line
        self.visible = True
        self.addParam(resource.LinkParam("title", "OS resource"))

    def render_GET(self, request):
        response = coap.Message(code=coap.CONTENT, payload='%s' % (self.mess,))
        return defer.succeed(response)

# Resource tree creation
log.startLogging(sys.stdout)
root = resource.CoAPResource()

well_known = resource.CoAPResource()
root.putChild('.well-known', well_known)
core = CoreResource(root)
well_known.putChild('core', core)

counter = CounterResource(5000)
root.putChild('counter', counter)

temperature = TempResources()
root.putChild('temperature', temperature)

time = TimeResource()
root.putChild('time', time)

other = resource.CoAPResource()
root.putChild('other', other)

block = BlockResource()
other.putChild('block', block)

cpu = CPUResources()
root.putChild('cpu', cpu)

disk = DiskResources()
root.putChild('disk', disk)

os = OSResources()
root.putChild('os', os)

separate = SeparateLargeResource()
other.putChild('separate', separate)

endpoint = resource.Endpoint(root)
reactor.listenUDP(coap.COAP_PORT, coap.Coap(endpoint)) #, interface="::")
reactor.run()
