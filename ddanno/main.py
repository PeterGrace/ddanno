import click
import os
import logging
from datetime import datetime
import socket

def formulate_event(title, message, date, hostname,
                    priority, alert_type, tags):
    # _e{title.length,text.length}:title|text|d:date_happened|h:hostname|p:priority|t:alert_type|#tag1,tag2
    if hostname is None:
        hostname = os.uname()[1]

    if date is None:
        date = datetime.now()
    eventstr = ("_e{{{title_len},{message_len}}}:{title}"
        "|{message}|d:{date}|h:{hostname}|p:{priority}"
        "|t:{alert}|{taglist}").format(
                    title_len=len(title),
                    message_len=len(message),
                    title=title,
                    message=message,
                    date=date,
                    hostname=hostname,
                    priority=priority,
                    alert=alert_type,
                    taglist=tags)
    return eventstr

def send_statsd_datagram(event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(event, "utf-8"), ("127.0.0.1", 8125))


@click.command()
@click.argument("title")
@click.argument("message")
@click.option("--date", default=None, help="date event happened")
@click.option("--hostname", default=None, help="hostname to correlate event")
@click.option("--priority", default="normal", help="priority to store event")
@click.option("--alert_type", default="info", help="what type of event")
@click.option("--tags", default=None, help=("comma-separated list of tags"
        "to apply to this annotation"))
@click.option("--debug/--no-debug", default=False, help="enable debugging")
@click.option("--dry-run/--no-dry-run", default=False, help=("just show message, "
        "don't send to host."))
def main(title, message, date, hostname, priority, alert_type, tags, debug, dry_run):
    if debug is True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARN)


    event = formulate_event(title, message, date, hostname,
                            priority, alert_type, tags)
    if dry_run is True:
        print(event)
    else:
        send_statsd_datagram(event)



if __name__ == '__main__':
    main()
