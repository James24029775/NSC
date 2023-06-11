from mininet.topo import Topo
import os

class MyTopo( Topo ):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        h1 = self.addHost( 'h1', ip='10.0.0.1' )
        h2 = self.addHost( 'h2', ip='10.0.0.2' )
        h3 = self.addHost( 'h3', ip='10.0.0.3' )
        h4 = self.addHost( 'h4', ip='10.0.0.4' )
        s1 = self.addSwitch( 's1' )
        
        # Add links
        self.addLink( s1, h1 )
        self.addLink( s1, h2 )
        self.addLink( s1, h3 )
        self.addLink( s1, h4 )

topos = { 'mytopo': ( lambda: MyTopo() ) }
