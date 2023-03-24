"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

# Feel free to add as many imports as you want.
from random import randint
from typing import (
    Set,
    Tuple,
)

from secret_sharing import (
    share_secret,
    Share, FIELD_MODULUS,
)


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        self.beaver_triplets = {}
        self.clients = {}

    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

        # We identify the participants by their index in the list of participants, not their client_id.
        self.clients[participant_id] = len(self.participant_ids) - 1

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """
        # If the triplet for the operation has not been generated yet, generate it.
        # An operation is identified by its id (op_id)
        if op_id not in self.beaver_triplets:
            self.beaver_triplets[op_id] = BeaverTriplet(len(self.participant_ids))

        return self.beaver_triplets[op_id].get_shares(self.clients[client_id])


class BeaverTriplet:
    """ Creates and holds beaver triplet shares for given number of participants. """

    def __init__(self, num_participants) -> None:
        self.a = randint(0, FIELD_MODULUS - 1)
        self.b = randint(0, FIELD_MODULUS - 1)
        self.c = self.a * self.b % FIELD_MODULUS

        self.a_shares = share_secret(self.a, num_participants)
        self.b_shares = share_secret(self.b, num_participants)
        self.c_shares = share_secret(self.c, num_participants)

    def get_shares(self, client_id) -> Tuple[Share, Share, Share]:
        return self.a_shares[client_id], self.b_shares[client_id], self.c_shares[client_id]
