import requests
import logging
import re

logging.basicConfig(level=logging.WARNING)

sblist = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
ignorelist = "ignorelist.txt"
destination = "stevenblack.conf"

def get_hosts():
    domains = []

    regex = re.compile(r'^0\.0\.0\.0\s+(.+)$')
    logging.debug("Getting list from {}".format(sblist))
    resp = requests.get(sblist)

    if resp.status_code != 200:
        logging.error("{} error when trying to retreive list from {}".format(resp.status_code, sblist))
        return
        
    for line in resp.text.split("\n"):
        line = line.strip()
        if line == "":
            logging.debug("Skipping empty line")
            continue
        if line[:1] == "#":
            logging.debug("Skipping line: {}".format(line))
            continue
        matches = regex.match(line)
        if not matches:
            logging.debug("Something wrong with line {}".format(line))
            continue
        logging.debug("Processing line {}".format(line))
        
        domains.append(matches.group(1))
    
    with open(ignorelist, "r") as fh:
        for line in fh.readlines():
            line = line.strip()
            try:
                domains.remove(line)
                logging.debug("removed {}".format(line))
            except ValueError:
                logging.warning("{} not found in blocklist".format(line))

    with open(destination, "w") as fh:
        for domain in domains:
            fh.write('local-zone: "{}" redirect\n'.format(domain))
            fh.write('local-data: "{}" A 0.0.0.0\n\n'.format(domain))

if __name__ == "__main__":
    get_hosts()