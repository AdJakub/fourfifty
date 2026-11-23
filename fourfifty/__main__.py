from collections import Counter
import argparse


from fourfifty.simulator import SimConfig, simulate
from fourfifty.baseline import recipients_per_sender, valid_mboxes
from fourfifty.bloom import BloomFilter

def main():
    parser = argparse.ArgumentParser(description="fourfifty mail traffic simulator")
    parser.add_argument("--duration", type=float, default=600.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--plot", action="store_true", help="save graphs as PNG files")
    args = parser.parse_args()
    config = SimConfig(duration=args.duration,seed=args.seed)
    events = list(simulate(config))
    bloom = BloomFilter(m=config.n_mailboxes*10, k=7)
    for address in valid_mboxes(config):
        bloom.add(address)
    misses = Counter(event.mail_from for event in events if event.rcpt_to not in bloom)
    total = len(events)
    labels = Counter(event.label for event in events)
    print("TOTAL MAIL TRAFFIC BY EVENT TYPE")
    print("-"*32)
    print(f"{'type':<12}{'events':>10}{'share':>10}")
    print("-"*32)
    for label, count in labels.most_common():
        print(f"{label.value:<12}{count:>10,}{count / total:>10.1%}")
    print("-"*32)
    print(f"{'total':<12}{total:>10,}")
    print(f"\n"*3)
    print("TOP SENDERS BY DIFFERENT RECIPIENTS")
    print("-"*44)
    print(f"{'sender':<32}{'recipients':>12}")
    print("-"*44)
    for sender, count in recipients_per_sender(events).most_common(5):
        print(f"{sender:<32}{count:>12,}")
    print(f"\n"*3)
    print("TOP SENDERS BY MAIL TO NONEXISTENT ADDRESSES")
    print("-"*44)
    print(f"{'sender':<32}{'misses':>12}")
    print("-"*44)
    for sender, count in misses.most_common(5):
        print(f"{sender:<32}{count:>12,}")


    if args.plot:
        try:
            from fourfifty.plots import plot_total, plot_recipients
        except ImportError:
            print("plotting requires matplotlib: pip install 'fourfifty[plot]'")
            return
        plot_total(events, config, "total.png")
        plot_recipients(events, "recipients.png")
        print("saved graphs: total.png, recipients.png")

if __name__ == "__main__":
    main()