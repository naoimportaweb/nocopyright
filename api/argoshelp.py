#!/usr/bin/env python3
# Download all packages into current directory

import json, os, sys, requests
import subprocess

DOWNLOAD_DIR = os.path.expandvars("$HOME/tmp/argos/");
if not os.path.exists( DOWNLOAD_DIR ):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True);

INDEX_JSON = os.path.join(os.path.expandvars("$HOME/desenv/nocopyright/data/"), "index.json");
with open(INDEX_JSON) as index_file:
    index = json.load(index_file)
    for metadata in index:
        if os.path.exists( os.path.join( DOWNLOAD_DIR, metadata["code"] + ".argosmodel" ) ):
            continue;
        links = metadata["links"]
        link = links[0]
        subprocess.run(["wget", link, "-P", DOWNLOAD_DIR])