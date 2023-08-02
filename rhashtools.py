import os, sys
import re
import hashlib
import argparse
from colorama import Fore, Style

fout = sys.stdout
diffmode = False
diffmap = {}

def getopparser():
    parser = argparse.ArgumentParser(description="OP")
    parser.add_argument("-d", "--diff", dest="diff", help="")
    parser.add_argument("-p", "--parse", dest="parse", help="")
    parser.add_argument("-o", "--output", dest="output", help="")
    return parser

def parsediff(filepath):
    hformat = re.compile(r"(.+)[|](.+)\n")
    with open(filepath, "r", encoding="utf-8") as f:
        while line := f.readline():
            if g := hformat.match(line):
                diffmap[g.group(1)] = g.group(2)

def search_recursive(directory, callback):
    for root, _, files in os.walk(directory):
        for file in files:
            callback(os.path.join(root, file))

def gethash(filepath, algorithm="sha256"):
    hash_obj = hashlib.new(algorithm)
    
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()

def writehash(filename):
    hashing = gethash(filename)
    fout.write(f"{filename}|{hashing}\n")

    if diffmode:
        if filename not in diffmap:
            sys.stderr.write(f"{Fore.RED}[Warning] New file detected! ({filename}) {Fore.RESET}\n")
        elif diffmap[filename] != hashing:
            sys.stderr.write(f"{Fore.RED}[Warning] Filehash is unmatched! ({filename}) {Fore.RESET}\n")
            sys.stderr.write(f"{Fore.RED}\t'{diffmap[filename]}' -> '{hashing}'{Fore.RESET}\n")
            diffmap.pop(filename)
        elif diffmap[filename] == hashing:
            diffmap.pop(filename)

if __name__ == "__main__":
    showhelp = True
    opparser = getopparser()
    args = getopparser().parse_args()

    if args.output:
        fout = open(args.output, "w", encoding="utf-8")

    if args.diff:
        showhelp = False
        diffmode = True
        parsediff(args.diff)

    if args.parse:
        showhelp = False
        search_recursive(args.parse, writehash)
        if diffmode:
            sys.stderr.write(f"{Fore.RED}") 
            for key, _ in diffmap.items():
                sys.stderr.write(f"[Warning] File is missing! ({key})")
            sys.stderr.write(f"{Fore.RESET}")

    if args.output:
        fout.close()
        fout = sys.stdout
    
    if showhelp:
        opparser.print_usage()