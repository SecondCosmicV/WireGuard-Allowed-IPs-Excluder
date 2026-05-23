import ipaddress
import sys
from pathlib import Path

# Usage:
# $ mkdir subnet_masks
# make txt files in it where each line is a comma-separated subnet mask list in CIDR notation
# Python-like comments are allowed
# example: $ python3 WireGuard_Excluded_IPs.py "f('file3',f('file1','file2'))"
# first arg for f is allowed ips, second is disallowed ips


def parse_ip_networks(ip_list_str):
    ip_list = ip_list_str.split(",")
    networks = []
    invalid_ip_addresses = []  # List to store invalid IPs.

    for ip in ip_list:
        ip = ip.strip()
        try:
            if "/" in ip:
                networks.append(ipaddress.ip_network(ip, strict=False))
            else:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version == 4:
                    networks.append(ipaddress.ip_network(f"{ip}/32", strict=False))
                else:
                    networks.append(ipaddress.ip_network(f"{ip}/128", strict=False))
        except ValueError:
            invalid_ip_addresses.append(ip)  # Add invalid IP to the list.

    return networks, invalid_ip_addresses  # Return both valid networks and invalid IPs.


def get_input_and_parse(prompt):
    while True:  # Keep looping until we break out.
        user_input = input(prompt)
        networks, invalid_ip_addresses = parse_ip_networks(
            user_input
        )  # Get both valid networks and invalid IPs.

        if not invalid_ip_addresses:  # If there are no invalid IPs, break the loop.
            break

        # If there are invalid IPs, notify the user and continue the loop.
        print("Invalid IPs or subnets: " + ", ".join(invalid_ip_addresses))
        print("Please try again. Ctrl+C to exit.")

    return networks


def exclude_networks(allowed_networks, disallowed_networks):
    remaining_networks = set(allowed_networks)

    for disallowed in disallowed_networks:
        new_remaining_networks = set()

        for allowed in remaining_networks:
            if allowed.version == disallowed.version:
                if disallowed.subnet_of(allowed):
                    # If the disallowed network is a subnet of the allowed network, exclude it
                    new_remaining_networks.update(allowed.address_exclude(disallowed))
                elif allowed.overlaps(disallowed):
                    # Handle partial overlap
                    new_remaining_networks.update(
                        handle_partial_overlap(allowed, disallowed)
                    )
                else:
                    # If there's no overlap, keep the allowed network as it is.
                    new_remaining_networks.add(allowed)
            else:
                # If the IP versions don't match, keep the allowed network as it is.
                new_remaining_networks.add(allowed)

        # Update the remaining networks after processing each disallowed network
        remaining_networks = new_remaining_networks

    return remaining_networks


def handle_partial_overlap(allowed, disallowed):
    # This function will handle the case of a partial overlap and return the non-overlapping portions of the allowed network.
    non_overlapping_networks = []

    # Calculate the IPs for the allowed and disallowed networks
    allowed_ips = list(allowed.hosts())
    disallowed_ips = set(disallowed.hosts())  # Use a set for faster lookup

    # Filter out the disallowed IPs
    allowed_ips = [ip for ip in allowed_ips if ip not in disallowed_ips]

    if not allowed_ips:
        # If no IPs are left, there's nothing to add
        return non_overlapping_networks

    # Create new network(s) from the remaining IPs.
    # This is a simplistic way and works on individual IPs, not ranges.
    # You might need a more efficient way to handle ranges of IPs, especially for large networks.
    for ip in allowed_ips:
        if ip.version == 4:
            non_overlapping_networks.append(
                ipaddress.ip_network(f"{ip}/32", strict=False)
            )
        else:
            non_overlapping_networks.append(
                ipaddress.ip_network(f"{ip}/128", strict=False)
            )

    return non_overlapping_networks


def sort_networks(networks):
    """Sort IP networks with all IPv4 first, then IPv6, each from lowest to highest."""
    ipv4 = []
    ipv6 = []
    for net in networks:
        if net.version == 4:
            ipv4.append(net)
        else:
            ipv6.append(net)
    # Sort each list individually
    ipv4_sorted = sorted(ipv4, key=lambda ip: ip.network_address)
    ipv6_sorted = sorted(ipv6, key=lambda ip: ip.network_address)

    # Combine the lists with all IPv4 addresses first, then IPv6
    return ipv4_sorted + ipv6_sorted

def file2input(fn):
    with open(Path('subnet_masks')/f'{fn}.txt','r') as f:
        return ','.join(filter(lambda x:x and x[0]!='#',map(lambda x:x.strip(),f.read().strip().splitlines())))

def f(inp1,inp2):
    if type(inp1) is str:
        allowed_input=file2input(inp1)
        allowed_networks, invalid_allowed = parse_ip_networks(allowed_input)
        assert not invalid_allowed
    else:
        allowed_networks=inp1
    if type(inp2) is str:
        disallowed_input=file2input(inp2)
        disallowed_networks, invalid_disallowed = parse_ip_networks(disallowed_input)
        assert not invalid_disallowed
    else:
        disallowed_networks=inp2
    excluded_allowed_networks = exclude_networks(allowed_networks, disallowed_networks)
    sorted_networks = sort_networks(excluded_allowed_networks)
    return sorted_networks

def main(unittest=False):
    sorted_networks = eval(sys.argv[1])
    print("AllowedIPs = " + ", ".join(map(str, sorted_networks)))

    if unittest:
        return sorted_networks


if __name__ == "__main__":
    main()

