from collections import Counter, defaultdict
from fourfifty.simulator import sender_address

def emails_per_sender(events):
    counts = Counter(event.mail_from for event in events)
    return counts

def recipients_per_sender(events):
    recipients = defaultdict(set)
    for event in events:
        recipients[event.mail_from].add(event.rcpt_to)
    counts = Counter({sender: len(rcpts) for sender, rcpts in recipients.items()})
    return counts

def valid_mboxes(config):
    mboxes = {sender_address(k) for k in range(config.n_mailboxes)}
    return mboxes