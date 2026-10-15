#!/usr/bin/env python3
"""Generate per-payload-size Contiki-NG probe sources and COOJA .csc scenarios.

Run this from inside a copy of ``cooja/apps/qhsg-udp`` placed in a Contiki-NG
tree (``examples/qhsg-udp``).  It writes ``qhsg-probe-<L>.c`` and
``qhsg-frag-<L>.csc`` for each payload length, using absolute paths that are
valid inside the ``contiker/contiki-ng`` container when the app lives at
``/home/user/contiki-ng/examples/qhsg-udp``.
"""
import os

PAYLOAD_LENGTHS = (64, 128, 256, 512, 1024, 1232, 2272)

# Path of the Contiki-NG tree *inside the COOJA container*.  The generated
# .csc files record absolute result-log paths that are valid in that context.
CONTAINER_CONTIKI = os.environ.get("QHSG_CONTAINER_CONTIKI", "/home/user/contiki-ng")

MOTEIFS = """      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiVib</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiIPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiButton</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiPIR</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiLED</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiCFS</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiEEPROM</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>"""


def mote_xml(mid, x, y, mtype):
    return f"""    <mote>
      <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>{x}</x>
        <y>{y}</y>
        <z>0.0</z>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiMoteID
        <id>{mid}</id>
      </interface_config>
      <interface_config>
        org.contikios.cooja.contikimote.interfaces.ContikiRadio
        <bitrate>250.0</bitrate>
      </interface_config>
      <motetype_identifier>{mtype}</motetype_identifier>
    </mote>"""


def motetype(ident, desc, source, cmd):
    return f"""    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <identifier>{ident}</identifier>
      <description>{desc}</description>
      <source>{source}</source>
      <commands>{cmd}</commands>
{MOTEIFS}
    </motetype>"""


def generate_csc(length, here):
    logpath = f"{CONTAINER_CONTIKI}/examples/qhsg-udp/results-{length}.txt"
    txt = f"""<?xml version="1.0" encoding="UTF-8"?>
<simconf>
  <simulation>
    <title>QHSG 6LoWPAN fragmentation probe (len={length})</title>
    <randomseed>123456</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>50.0</transmitting_range>
      <interference_range>100.0</interference_range>
      <success_ratio_tx>1.0</success_ratio_tx>
      <success_ratio_rx>1.0</success_ratio_rx>
    </radiomedium>
    <events>
      <logoutput>40000</logoutput>
    </events>
"""
    txt += motetype("mtypeRoot", "RPL root / UDP server",
                    "[CONTIKI_DIR]/examples/qhsg-udp/qhsg-server.c",
                    "$(MAKE) -j$(CPUS) qhsg-server.cooja TARGET=cooja") + "\n"
    txt += motetype("mtypeProbe", f"QHSG probe client (len={length})",
                    f"[CONTIKI_DIR]/examples/qhsg-udp/qhsg-probe-{length}.c",
                    f"$(MAKE) -j$(CPUS) qhsg-probe-{length}.cooja TARGET=cooja") + "\n"
    txt += mote_xml(1, 40.0, 40.0, "mtypeRoot") + "\n"
    txt += mote_xml(2, 30.0, 40.0, "mtypeProbe") + "\n"
    script = (
        'TIMEOUT(900000);\n'
        f'log.writeFile("{logpath}", "run_start len={length}\\n");\n'
        'while(true) {\n'
        '  WAIT_UNTIL(true);\n'
        f'  log.append("{logpath}", id + "|" + msg + "\\n");\n'
        '  if(msg.contains("QHSG done")) {\n'
        '    log.testOK();\n'
        '  }\n'
        '  YIELD();\n'
        '}\n'
    )
    txt += """  </simulation>
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter>Probe</filter>
      <formatted_time />
    </plugin_config>
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>""" + script + """</script>
      <active>true</active>
    </plugin_config>
  </plugin>
</simconf>
"""
    return txt


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "qhsg-probe.c")) as f:
        body = f.read()
    for length in PAYLOAD_LENGTHS:
        src = body.replace("#define QHSG_PAYLOAD_LEN 64",
                           "#define QHSG_PAYLOAD_LEN %d" % length)
        with open(os.path.join(here, f"qhsg-probe-{length}.c"), "w") as f:
            f.write(src)
        with open(os.path.join(here, f"qhsg-frag-{length}.csc"), "w") as f:
            f.write(generate_csc(length, here))
        print(f"wrote qhsg-probe-{length}.c and qhsg-frag-{length}.csc")


if __name__ == "__main__":
    main()
