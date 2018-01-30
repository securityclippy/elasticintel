#!/usr/bin/env python3

from whois import LambdaWhois


def handler(event, context):
    lw = LambdaWhois(chunk=50, thread_timeout=2, verbose_logging=False)
    items = lw.get_items_to_update()
    if len(items) > 0 :
        lw.lookup_and_upload(items)
    else:
        print("No items to lookup.  Exiting...")
        return

