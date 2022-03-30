import hashlib
import math
import os
import random
from datetime import datetime, timedelta
from functools import reduce

import numpy as np
import pandas as pd
from faker import Faker


class GenerateData:
    def __init__(self, num_users, num_txn, fraud_ratio, start_date, end_date):
        self.num_users = num_users
        self.num_txn = num_txn
        self.faker = Faker()
        self.seed = 123
        random.seed(self.seed)
        np.random.seed(self.seed)
        self.faker.seed_locale("en_US", 0)
        self.faker.seed_instance(self.seed)
        self.srtf = "%Y-%m-%d %H:%M:%S"
        self.start_date = start_date
        self.end_date = end_date
        self.distribution = {
            0.05: (0.01, 1.01),
            0.075: (1, 11.01),
            0.525: (10, 100.01),
            0.25: (100, 1000.01),
            0.10: (1000, 10000.01),
        }
        self.fraud_ratio = fraud_ratio
        self.chain_attack = sorted(random.sample(range(3, 11), 8))
        self.data = []

    def generate_cc_num(self):
        cc_num = set()
        for _ in range(self.num_users):
            cc_id = self.faker.credit_card_number(card_type="visa")
            cc_num.add(cc_id)
        return list(cc_num)

    def generate_timestamps(self):
        start = datetime.strptime(self.start_date, self.srtf)
        end = datetime.strptime(self.end_date, self.srtf)
        timestamps = [
            self.faker.date_time_between(
                start_date=start, end_date=end, tzinfo=None
            ).strftime(self.srtf)
            for _ in range(self.num_txn)
        ]
        return timestamps

    def generate_transaction_amount(self):
        amt = []
        for key, value in self.distribution.items():
            start, end = value
            n = int(self.num_txn * key)
            for _ in range(n):
                amt.append(round(np.random.uniform(start, end)))
        random.shuffle(amt)
        return amt

    def generate_transaction_id(self, timestamp, cc_num, amt):
        hashing = f"{timestamp}{cc_num}{amt}"
        digest = hashlib.md5(hashing.encode("utf-8")).hexdigest()
        return digest

    def generate_transactions(self):
        chain = self.create_fraud_chain_attack()
        cc_num = self.generate_cc_num()
        timestamps = self.generate_timestamps()
        amts = self.generate_transaction_amount()
        for timestamp, amt in zip(timestamps, amts):
            cc = random.choice(cc_num)
            txn = self.generate_transaction_id(timestamp, cc, amt)
            self.data.append(
                {"txn_id": txn, "cc_num": cc, "ts": timestamp, "amt": amt, "label": 0,}
            )
        self.inject_fraud_txn(chain)
        transactions = pd.DataFrame(self.data)
        return transactions

    def chain_length(self, chain):
        length = reduce(lambda count, l: count + len(l), chain, 0)
        return length

    def create_fraud_chain_attack(self):
        num_attacks = int(self.fraud_ratio * self.num_txn)
        chains = []
        check_duplicates = set()
        while self.chain_length(chains) < num_attacks:
            idx = random.choice(range(self.num_txn))
            chain_length = random.choice(self.chain_attack)
            if idx not in check_duplicates:
                freq = []
                check_duplicates.add(idx)
                freq.append(idx)
                for i in range(1, chain_length):
                    if idx + i not in check_duplicates:
                        if self.chain_length(chains) == num_attacks:
                            break
                        freq.append(idx + i)
                        check_duplicates.add(idx + i)
                chains.append(freq)
        return chains

    def generate_timestamps_for_fraud_attacks(self, timestamp, chain_length):
        timestamps = []
        timestamp = datetime.strptime(timestamp, self.srtf)
        for _ in range(chain_length):
            delta = random.randint(30, 120)
            current = timestamp + timedelta(seconds=delta)
            timestamps.append(current.strftime(self.srtf))
            timestamp = current
        return timestamps

    def generate_amounts_for_fraud_attacks(self, chain_length):
        amounts = []
        for percentage, span in self.distribution.items():
            n = math.ceil(chain_length * percentage)
            start, end = span
            for _ in range(n):
                amounts.append(round(np.random.uniform(start, end + 1), 2))
        return amounts[:chain_length]

    def inject_fraud_txn(self, chain):
        for idx in chain:
            start_chain_id = idx.pop(0)
            txn = self.data[start_chain_id]
            ts = txn["ts"]
            cc_num = txn["cc_num"]
            amt = txn["amt"]
            txn["label"] = 1
            inject_ts = self.generate_timestamps_for_fraud_attacks(ts, len(idx))
            inject_amt = self.generate_amounts_for_fraud_attacks(len(idx))
            random.shuffle(inject_amt)
            for i, j in enumerate(idx):
                original_transaction = self.data[j]
                inject_timestamp = inject_ts[i]
                original_transaction["ts"] = inject_timestamp
                original_transaction["label"] = 1
                original_transaction["cc_num"] = cc_num
                original_transaction["amt"] = inject_amt[i]
                original_transaction["txn_id"] = self.generate_transaction_id(
                    inject_timestamp, cc_num, amt
                )
                self.data[j] = original_transaction


if __name__ == "__main__":
    dataset = GenerateData(
        10000, 6000000, 0.0025, "2021-08-01 00:00:00", "2022-02-01 00:01:00"
    )

    df = dataset.generate_transactions()
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    df.to_csv(f"{data_dir}/transactions.csv", index=False)
