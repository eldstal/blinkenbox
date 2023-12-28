import wifi



def ifconfig():
    return (
        wifi.radio.ipv4_address,
        wifi.radio.ipv4_subnet,
        wifi.radio.ipv4_gateway,
        wifi.radio.ipv4_dns
        )


def try_connect(networks):

    wifi.radio.enabled = False
    wifi.radio.enabled = True

    try_time = 10
    while True:

        for net in networks:
            print(f"Attempting connection to {net['ssid']}...")
            wifi.radio.connect(net["ssid"], net["psk"])

            for wait in range(try_time):
                #self.flash(0.25,0.75)
                if wifi.radio.connected:
                    print(f"Connected to {net['ssid']}!")
                    print(str(ifconfig()))
                    return

        if try_time < 30:
            try_time += 5


def loop_with_net(func):
    while wifi.radio.connected:
        func()

