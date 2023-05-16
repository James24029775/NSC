from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.term import makeTerm

if '__main__' == __name__:

	net = Mininet(controller=RemoteController)
	c0 = net.addController('c0',ip='127.0.0.1', port=6633)

	s1 = net.addSwitch( 's1' )
	s2 = net.addSwitch( 's2' )
	s3 = net.addSwitch( 's3' )	

	h1 = net.addHost( 'h1', mac='00:00:00:00:00:01')
	h2 = net.addHost( 'h2', mac='00:00:00:00:00:02')
	h3 = net.addHost( 'h3', mac='00:00:00:00:00:03')
	h4 = net.addHost( 'h4', mac='00:00:00:00:00:04')
	h5 = net.addHost( 'h5', mac='00:00:00:00:00:05')
	h6 = net.addHost( 'h6', mac='00:00:00:00:00:06')
	h7 = net.addHost( 'h7', mac='00:00:00:00:00:07')
	h8 = net.addHost( 'h8', mac='00:00:00:00:00:08')

	net.addLink( s1, h1 )
	net.addLink( s1, h2 )
	net.addLink( s1, h3 )
	net.addLink( s2, h4 )
	net.addLink( s2, h5 )
	net.addLink( s3, h6 )
	net.addLink( s3, h7 )
	net.addLink( s3, h8 )
	net.addLink( s1, s2 )
	net.addLink( s2, s3 )
	# net.addLink( s3, s1 )

	net.build()
	c0.start()
	s1.start([c0])
	s2.start([c0])
	s3.start([c0])

	net.terms.append(makeTerm(s1))
	net.terms.append(makeTerm(s2))
	net.terms.append(makeTerm(s3))
	
	net.start()
	CLI(net)
	net.stop()