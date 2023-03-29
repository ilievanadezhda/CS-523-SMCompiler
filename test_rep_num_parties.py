"""
Integration tests for the report analysis.
"""

import time
from multiprocessing import Process, Queue
from random import randint

from expression import Secret
from protocol import ProtocolSpec
from secret_sharing import FIELD_MODULUS
from server import run
from smc_party import SMCParty

BYTES_KEY = "bytes"
TIME_KEY = "time_s"


def smc_client(client_id, prot, value_dict, queue):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    cli.run()
    queue.put({BYTES_KEY: cli.bytes_consumed, TIME_KEY: cli.time_consumed})
    # print(f"{client_id} total bytes: " + str(cli.bytes_consumed))
    # print(f"{client_id} total time: " + str(cli.time_consumed))


def smc_server(args):
    run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue)) for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        results.append(queue.get())

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)
    return results


def suite(parties, expr, repeat_test: int = 1):
    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    experiment_sub_results = []
    for i in range(repeat_test):
        results = run_processes(participants, *clients)

        # calculate max(time_ms)
        longest_time = max(entry[TIME_KEY] for entry in results)

        # calculate sum(bytes)
        total_bytes = sum(entry[BYTES_KEY] for entry in results)

        # print("Execution time: i=" + str(i) + ": " + str(longest_time))
        # print("Total bytes consumed: i=" + str(i) + ": " + str(total_bytes))

        experiment_sub_results.append({BYTES_KEY: total_bytes, TIME_KEY: longest_time})

    return experiment_sub_results


def test_num_parties_effect():
    # how many times to execute protocol and compute average bytes and time to report for specified number of parties
    num_repeats = 10
    num_parties = [2, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    f = open("report_csv_files/rep_num_parties.csv", "at")
    f.write("number_of_parties,computation_cost,communication_cost\n")
    for parties in num_parties:
        res = execute_test(num_parties=parties, num_repeats=num_repeats)
        # report computation cost in seconds and communication cost in kilobytes
        for subres in res:
            f.write(str(parties) + "," + str(subres[TIME_KEY]) + "," + str(subres[BYTES_KEY] / 1024) + "\n")
    f.close()


def execute_test(num_parties: int = 2, num_repeats: int = 3):
    secrets = []
    parties = {}

    for i in range(num_parties):
        sec_i = Secret()
        secrets.append(sec_i)
        parties["party" + str(i)] = {sec_i: randint(0, FIELD_MODULUS - 1)}

    expr = secrets[0]
    for i in range(num_parties):
        if i != 0:
            expr = expr + secrets[i]
    return suite(parties, expr, num_repeats)
