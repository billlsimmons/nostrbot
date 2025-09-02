import os, time, logging, feedparser, pathlib, sys

# Nostr
from pynostr.key import PrivateKey
from pynostr.event import Event
from pynostr.relay_manager import RelayManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

RSS_URL = os.getenv("RSS_URL")
NSEC = os.getenv("NOSTR_NSEC")
RELAYS = [r.strip() for r in os.getenv("NOSTR_RELAYS", "wss://relay.damus.io,wss://nos.lol,wss://relay.snort.social,wss://relay.primal.net,wss://nostr.mom").split(",") if r.strip()]
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "0"))  # 0 for one-shot in CI
STATE_FILE = os.getenv("STATE_FILE", "state/last_id.txt")

def ensure_state_dir():
    p = pathlib.Path(STATE_FILE).parent
    p.mkdir(parents=True, exist_ok=True)

def read_last_id():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def write_last_id(val: str):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(val)

class NostrPublisher:
    def __init__(self, nsec: str, relays: list[str]):
        if nsec.startswith("nsec"):
            self.sk = PrivateKey.from_nsec(nsec)
        else:
            self.sk = PrivateKey(nsec)  # treat as hex
        self.rm = RelayManager(timeout=8)
        for r in relays:
            self.rm.add_relay(r)
        self.rm.run_sync()
        logging.info(f"Connected to {len(relays)} relays")

    def publish(self, content: str):
        ev = Event(content)
        ev.sign(self.sk.hex())
        self.rm.publish_event(ev)
        time.sleep(1.0)

def normalize_id(entry):
    # use link as stable id
    return entry.link

def run_once():
    assert RSS_URL, "Missing RSS_URL"
    assert NSEC, "Missing NOSTR_NSEC"
    assert RELAYS, "Missing NOSTR_RELAYS"

    ensure_state_dir()
    last_id = read_last_id()

    pub = NostrPublisher(NSEC, RELAYS)
    feed = feedparser.parse(RSS_URL)
    items = getattr(feed, "entries", [])
    # Process oldest->newest
    items_sorted = sorted(items, key=lambda e: e.get("published_parsed") or time.gmtime(0))
    posted = 0
    for e in items_sorted:
        eid = normalize_id(e)
        # if last_id exists, only post items strictly newer (string compare is ok for equal link patterns)
        if last_id and eid <= last_id:
            continue
        title = (e.get("title") or "").strip()
        link = (e.get("link") or "").strip()
        if not link:
            continue
        body = f"Bill Simmons on X:\n\n{title}\n\nLink: {link}"
        pub.publish(body)
        last_id = eid
        posted += 1
        write_last_id(last_id)
        logging.info(f"Posted {link}")
    logging.info(f"Done. New posts: {posted}")
    return posted

def main():
    # In CI: run once. Locally: loop if POLL_SECONDS > 0
    if POLL_SECONDS <= 0:
        run_once()
    else:
        while True:
            try:
                run_once()
            except Exception as ex:
                logging.exception(f"Loop error: {ex}")
                time.sleep(10)
            time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    sys.exit(main())