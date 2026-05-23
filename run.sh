#!/usr/bin/env bash

guix shell --container python -- python3 WireGuard_Excluded_IPs.py "f(f(f('all','vpnip'),f('priv','dnsip')),'others')"

