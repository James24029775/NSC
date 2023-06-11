from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        h5 = self.addHost( 'h5', ip='10.0.0.5' )
        h6 = self.addHost( 'h6', ip='10.0.0.6' )
        h7 = self.addHost( 'h7', ip='10.0.0.7' )
        h8 = self.addHost( 'h8', ip='10.0.0.8' )
        s2 = self.addSwitch( 's2' )

        # Add links
        self.addLink( s2, h5 )
        self.addLink( s2, h6 )
        self.addLink( s2, h7 )
        self.addLink( s2, h8 )

topos = { 'mytopo': ( lambda: MyTopo() ) }