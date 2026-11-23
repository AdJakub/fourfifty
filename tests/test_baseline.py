from fourfifty.events import Event, Label
from fourfifty.baseline import emails_per_sender, recipients_per_sender, valid_mboxes
from fourfifty.simulator import SimConfig

def make_event(sender, rcpt):
    return Event(timestamp=0.0, client_ip='198.18.0.0', mail_from=sender, rcpt_to=rcpt, message_id=0, label=Label.NORMAL)

def test_emails_per_sender():
    events = [
        make_event("alice@x.example", "bob@x.example"),
        make_event("alice@x.example", "bob@x.example"),
        make_event("alice@x.example", "carol@x.example"),
        make_event("dave@x.example", "bob@x.example"),

    ]
    counts = emails_per_sender(events)
    assert counts["alice@x.example"] == 3
    assert counts["dave@x.example"] == 1

def test_recipients_per_sender():
    events = [
        make_event("alice@x.example", "bob@x.example"),
        make_event("alice@x.example", "bob@x.example"),
        make_event("alice@x.example", "carol@x.example"),
        make_event("dave@x.example", "bob@x.example"),

    ]
    counts = recipients_per_sender(events)
    assert counts["alice@x.example"] == 2
    assert counts["dave@x.example"] == 1

def test_valid_mboxes():
    mboxes = valid_mboxes(SimConfig(n_mailboxes=3))
    assert len(mboxes) == 3
    assert "user0@sender0.example" in mboxes
    assert "user3@sender3.example" not in mboxes