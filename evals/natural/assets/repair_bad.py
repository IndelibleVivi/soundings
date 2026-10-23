import json
import sys

def normalize(text):
    return list(dict.fromkeys(part.strip().lower() for part in text.split(',') if part.strip()))

if __name__=='__main__': print(json.dumps(normalize(sys.argv[1]),ensure_ascii=False))
