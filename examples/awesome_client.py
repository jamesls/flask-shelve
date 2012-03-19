#!/usr/bin/env python

import sys
import json
from argparse import ArgumentParser
from urllib2 import urlopen
from urllib import urlencode


def main():
    parser = ArgumentParser()
    parser.add_argument('-H', '--hostname', default='127.0.0.1:5000')
    parser.add_argument('--no-awesome', action="store_false",
                        dest="awesome")
    parser.add_argument('--awesome', action="store_true", default=True)
    parser.add_argument('-c', '--check-awesomeness',
                        action="store_true")
    parser.add_argument('-r', '--reset',
                        action="store_true")
    parser.add_argument('-v', '--verbose',
                        action="store_true")
    parser.add_argument('--url')
    args = parser.parse_args()
    if args.reset:
        f = urlopen('http://%s/reset/' % args.hostname, data='').read()
        return
    if args.url:
        content = urlopen(args.url).read()
    else:
        content = sys.stdin.read()
    if args.check_awesomeness:
        data = urlencode({'content': content})
        f = urlopen('http://%s/awesomeness/check/' % args.hostname, data=data).read()
        if args.verbose:
            print f
        else:
            print json.loads(f).get('is_awesome')
    else:
        data = {'is_awesome': args.awesome,
                'content': content}
        data = urlencode(data)
        f = urlopen('http://%s/awesomeness/' % args.hostname, data=data).read()
        print "Successfully sent to server."


if __name__ == '__main__':
    main()
