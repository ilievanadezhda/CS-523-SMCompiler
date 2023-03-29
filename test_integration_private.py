import time
from multiprocessing import Process, Queue

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run
from smc_party import SMCParty
from secret_sharing import FIELD_MODULUS


def smc_client(client_id, prot, value_dict, queue):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    res = cli.run()
    queue.put(res)
    print(f"{client_id} has finished!")


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

    print("Server stopped.")

    return results


def suite(parties, expr, expected):
    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    results = run_processes(participants, *clients)

    for result in results:
        assert result == expected


def test_mult0():
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()
    dave_secret = Secret()

    parties = {
        "Alice": {alice_secret: 5},
        "Bob": {bob_secret: 6},
        "Charlie": {charlie_secret: 2},
        "Dave": {dave_secret: 3},
    }

    expr = alice_secret * bob_secret + charlie_secret * dave_secret
    expected = 5 * 6 + 2 * 3
    suite(parties, expr, expected)


def test_mult1():
    alice_secret = Secret()
    bob_secret = Secret()
    dave_secret = Secret()

    parties = {
        "Alice": {alice_secret: 5},
        "Bob": {bob_secret: 6},
        "Dave": {dave_secret: 3},
    }

    expr = alice_secret * bob_secret * dave_secret
    expected = 5 * 6 * 3
    suite(parties, expr, expected)


def test_mult2():
    alice_secret = Secret()
    bob_secret = Secret()
    dave_secret = Secret()
    scalar = Scalar(5)

    parties = {
        "Alice": {alice_secret: 5},
        "Bob": {bob_secret: 6},
        "Dave": {dave_secret: 3},
    }

    expr = alice_secret * bob_secret * (dave_secret + scalar)
    expected = 5 * 6 * (3 + 5)
    suite(parties, expr, expected)


def test_mult3():
    alice_secret1 = Secret()
    alice_secret2 = Secret()

    parties = {
        "Alice": {alice_secret1: 3, alice_secret2: 5},
    }

    expr = alice_secret1 * alice_secret2
    expected = 3 * 5
    suite(parties, expr, expected)

def test_mult4():
    alice_secret1 = Secret()
    alice_secret2 = Secret()

    parties = {
        "Alice": {alice_secret1: 300, alice_secret2: 500},
    }

    expr = Scalar(10) * alice_secret1 * alice_secret2
    expected = (10 * 300 * 500) % FIELD_MODULUS
    suite(parties, expr, expected)

def test_mult5():
    alice_secret = Secret()
    bob_secret = Secret()
    dave_secret = Secret()

    parties = {
        "Alice": {alice_secret: 504},
        "Bob": {bob_secret: 64},
        "Dave": {dave_secret: 30},
    }

    expr = alice_secret * bob_secret * Scalar(10) * dave_secret  * Scalar(1000) * Scalar(1000)
    expected = (504 * 64 * 10 * 30 * 1000 * 1000) % FIELD_MODULUS
    suite(parties, expr, expected)

def test_suite0():
    """
    f(a, b) = a + b + K
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3000},
        "Bob": {bob_secret: 5000},
    }

    expr = alice_secret + bob_secret + Scalar(10)
    expected = (3000 + 5000 + 10) % FIELD_MODULUS
    suite(parties, expr, expected)


def test_suite1():
    """
    f(a, b) = K1 + K2
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14}
    }

    expr = (Scalar(1) + Scalar(2))
    expected = 1 + 2
    suite(parties, expr, expected)


def test_suite2():
    """
    f(a, b) = Ka - b
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 14},
        "Bob": {bob_secret: 3},
    }

    expr = (Scalar(2) * alice_secret - bob_secret)
    expected = 2 * 14 - 3
    suite(parties, expr, expected)


def test_suite3():
    """
    f(a, b, c) = a*K1*K2 + b + c
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}
    }

    expr = alice_secret * Scalar(2) * Scalar(3) + bob_secret + charlie_secret
    expected = 3 * 2 * 3 + 14 + 2
    suite(parties, expr, expected)


def test_suite4():
    """
    f(a, b) = K1 + K2*a*K3 + K4*b
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},

    }

    expr = Scalar(2) + Scalar(3) * alice_secret * Scalar(2) + Scalar(5) * bob_secret
    expected = 2 + 3 * 3 * 2 + 5 * 14
    suite(parties, expr, expected)


def test_suite5():
    """
    f(a, b, c) = a + b + c + (K1 + K2 + K3)
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = alice_secret + bob_secret + charlie_secret + (Scalar(2) + Scalar(3) + Scalar(5))
    expected = 3 + 14 + 2 + (2 + 3 + 5)
    suite(parties, expr, expected)


def test_suite6():
    """
    f(a, b, c) = K1 + K2 + K3 + K4 + K5 + K6
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = Scalar(2) + Scalar(3) + Scalar(5) + Scalar(2) + Scalar(3) + Scalar(5)
    expected = 2 + 3 + 5 + 2 + 3 + 5
    suite(parties, expr, expected)


def test_suite7():
    """
    f(a, b, c) = K1*K2
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = Scalar(2) * Scalar(3)
    expected = 2 * 3
    suite(parties, expr, expected)


def test_suite8():
    """
    f(a, b, c) = a + b + c + (K1 + K2 + K3*K4*K5)
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = alice_secret + bob_secret + charlie_secret + (Scalar(2) + Scalar(3) + Scalar(5) * Scalar(2) * Scalar(3))
    expected = 3 + 14 + 2 + (2 + 3 + 5 * 2 * 3)
    suite(parties, expr, expected)


def test_suite9():
    """
    f(a, b, c) = K1*K2*K3*K4*K5
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = Scalar(2) * Scalar(3) * Scalar(5) * Scalar(2) * Scalar(3)
    expected = 2 * 3 * 5 * 2 * 3
    suite(parties, expr, expected)


def test_suite10():
    """
    f(a, b, c) = K1
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = Scalar(2)
    expected = 2
    suite(parties, expr, expected)


def test_suite11():
    """
    f(a, b, c) = K1*K2*a
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = Scalar(2) * Scalar(3) * alice_secret
    expected = 2 * 3 * 3
    suite(parties, expr, expected)


def test_suite12():
    """
    f(a, b, c) = K1*a + K2*b + K3*c
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = Scalar(2) * alice_secret + Scalar(3) * bob_secret + Scalar(5) * charlie_secret
    expected = 2 * 3 + 3 * 14 + 5 * 2
    suite(parties, expr, expected)


def test_suite13():
    """
    f(a, b, c) = K1*a
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = Scalar(5) * alice_secret
    expected = 5 * 3
    suite(parties, expr, expected)


def test_suite14():
    """
    f(a, b, c) = K1*K2 + K3
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 14},
        "Charlie": {charlie_secret: 2}

    }

    expr = Scalar(5) * Scalar(3) + Scalar(2)
    expected = 5 * 3 + 2
    suite(parties, expr, expected)


def test_suite15():
    """
    f(a, b) = a + b + K1 + K2 + K3
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 113},
        "Bob": {bob_secret: 5},
    }

    expr = (alice_secret + bob_secret + Scalar(2) + Scalar(10) + Scalar(3))
    expected = 113 + 5 + 2 + 10 + 3
    suite(parties, expr, expected)


def test_suite16():
    """
    f(a, b) = (K1 + K2) * a
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 5},
        "Charlie": {charlie_secret: 7},
    }

    expr = (Scalar(10) + Scalar(5)) * alice_secret
    expected = (10 + 5) * 3
    suite(parties, expr, expected)


def test_suite17():
    """
    f(a, b) = (a * b)
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 3},
        "Bob": {bob_secret: 5}
    }

    expr = (alice_secret * bob_secret)
    expected = (3 * 5)
    suite(parties, expr, expected)


def test_suite18():
    """
    f(a_1, a_2) = (K - a_1) * a_2
    """
    alice_secret1 = Secret()
    alice_secret2 = Secret()

    parties = {
        "Alice": {alice_secret1: 3, alice_secret2: 5},
    }

    expr = Scalar(20) - alice_secret1 * alice_secret2
    expected = 20 - 3 * 5
    suite(parties, expr, expected)


def test_suite19():
    """
    f(a_1, a_2) = (K - a_1) * a_2
    """
    alice_secret1 = Secret()
    alice_secret2 = Secret()

    parties = {
        "Alice": {alice_secret1: 30000, alice_secret2: 5000},
    }

    expr = Scalar(2000) - alice_secret1 - alice_secret2
    expected = (2000 - 30000 - 5000) % FIELD_MODULUS
    suite(parties, expr, expected)

def test_suite20():
    """
    f(a, b) = K
    """
    alice_secret = Secret()
    bob_secret = Secret()

    parties = {
        "Alice": {alice_secret: 300},
        "Bob": {bob_secret: 500},
    }

    expr = Scalar(20000)
    expected = (20000) % FIELD_MODULUS
    suite(parties, expr, expected)

def test_suite21():
    """
    f(a, b, c, d) = (a*b + c + K1*d)*(c*a*K2 - K3 - b) + K4 - a*b*c*d
    """
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()
    dave_secret = Secret()
    parties = {
        "Alice": {alice_secret: 10},
        "Bob": {bob_secret: 20},
        "Charlie": {charlie_secret: 30},
        "Dave": {dave_secret: 40},
    }
    expr = (alice_secret * bob_secret + charlie_secret + Scalar(2) * dave_secret) * (charlie_secret * alice_secret * Scalar(3) - Scalar(4) - bob_secret) + Scalar(5) - alice_secret * bob_secret * charlie_secret * dave_secret
    expected = ((10 * 20 + 30 + 2 * 40) * (30 * 10 * 3 - 4 - 20) + 5 - 10 * 20 * 30 * 40) % FIELD_MODULUS
    suite(parties, expr, expected)
