import getpass
import logging
from pathlib import Path
from sys import version_info

from netmiko import ConnectHandler
from ntc_templates.parse import parse_output


# Make folders used for Lab 2
Path("logs").mkdir(exist_ok=True)
Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/reports").mkdir(parents=True, exist_ok=True)

# Lab Log Configuration
logging.basicConfig(
    filename="logs/lab.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def main():
    logging.info("LAB2_START")

    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    logging.info("CREDENTIALS_COLLECTED")
    print("Credentials entered successfully.")

    device = {
    "device_type": "cisco_ios",
    "host": "devnetsandboxiosxec8k.cisco.com",
    "username": username,
    "password": password,
    "port": 22,
    "timeout": 10,
    } 
    try:
        connection = ConnectHandler(**device)
        logging.info("CONNECT_OK")
        print("Connected to the Cisco device successfully!")

        commands = [
            "show version",
            "show ip interface brief",
            "show inventory",
        ]

        outputs = {}

        for command in commands:
            print(f"Running: {command}")
            output = connection.send_command(command)
            outputs[command] = output
            logging.info(f"CMD_RUN:{command}")

            filename = command.replace(" ", "_") + ".txt"
            filepath = Path("data/raw") / filename
            filepath.write_text(output)

        parsed_outputs = {}
        
        for command, output in outputs.items():
             try:
                parsed = parse_output(
                     platform="cisco_ios",
                     command=command,
                     data=output
                )

                if parsed: 
                    parsed_outputs[command] = parsed
                    logging.info(f"PARSE_OK:{command}")
                    print(f"Parsed successfully: {command}")
                else:
                    logging.error(f"PARSE_FAIL:{command}")
                    print(f"Parsing returned no data: {command}")

             except Exception as error:
                logging.error(f"PARSE_FAIL:{command}: {error}")
                print(f"Parsing failed for {command}: {error}")

        version_info = parsed_outputs["show version"][0]

        hostname = version_info.get("hostname", "Unknown")
        software_version = version_info.get("version", "Unknown")

        report = (
                f"Device Summary\n"
                f"==============\n"
                f"Hostname: {hostname}\n"
                f"Software Version: {software_version}\n"
            )

        print("\n" + report)

        report_path = Path("data/reports/device_summary.txt")
        report_path.write_text(report)

        logging.info("REPORT_SAVED")
        connection.disconnect()
        logging.info("LAB2_END")
        print("Disconnected from device.")

    except Exception as error:
        logging.error(f"CONNECT_FAIL: {error}")
        print(f"Connection failed: {error}")
        return 

if __name__ == "__main__":
    main()

