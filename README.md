# Tor-test

The code tests the performance of Tor when we download objects through Tor with a specific Exit policy. We want to evaluate if the Tor client selects the exit node of the circuits from a set of exit relays with a specific Exit Policy whether their experienced performance improves or not. 

We modified the Tor version tor-0.2.6.10 to select the exit relays among the relays that only support port 80 or 443 (or both). script.py launches our modified Tor, starts downloading an object from a given address, saves the download time, kills the Tor's process, and starts a new download.
