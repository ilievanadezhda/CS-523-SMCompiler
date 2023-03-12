"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

from typing import (
    Dict
)

import jsonpickle

from communication import Communication
from expression import (
    Expression,
    Secret, count_num_secrets, AddOperation, MultOperation
)
from message_utils import ShareMessage, SECRET_SHARE_LABEL, RESULT_SHARE_LABEL, ResultShareMessage, Message, \
    PUBLISH_RESULT_LABEL
from protocol import ProtocolSpec
from secret_sharing import (
    share_secret, Share, reconstruct_secret,
)

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
        ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict

    def is_leader(self) -> bool:
        """ Should the party do the operations that are done by one party exclusively. """
        return self.client_id == self.protocol_spec.participant_ids[0]

    def get_leader(self) -> str:
        """ Returns the leader client id. """
        return self.protocol_spec.participant_ids[0]

    def is_self(self, participant: str) -> bool:
        """ Is the current party the one with the provided client id. """
        return self.client_id == participant

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        participants = self.protocol_spec.participant_ids
        num_participants = len(participants)
        expression = self.protocol_spec.expr

        # share secrets that belong to this client
        personal_shares = {}
        for secret, value in self.value_dict.items():
            personal_shares[secret.id] = share_secret(value, num_participants)

        # send shares via private messages, including id and share value
        # and create map of secret Share(s) per ID
        shares_dict = {}
        for i in range(num_participants):
            for (id, shares) in personal_shares.items():
                if self.is_self(participants[i]):
                    shares_dict[id] = shares[i]
                else:
                    private_message = ShareMessage(id, shares[i])
                    self.comm.send_private_message(participants[i], SECRET_SHARE_LABEL, private_message.json_rep())

        # wait for private share messages from other parties
        total_messages_to_receive = count_num_secrets(expression) - len(personal_shares)
        for _ in range(total_messages_to_receive):
            received_share = self.comm.retrieve_private_message(SECRET_SHARE_LABEL)
            secret_share = jsonpickle.decode(received_share, classes=ShareMessage)
            shares_dict[secret_share.id] = secret_share.share

        # todo: do we need this step below ?
        # wait Start_Protocol message from all participants (excluding oneself)

        final_result_share = self.process_expression(expression, shares_dict)
        if self.is_leader():
            # wait for remaining final_result_share(s)
            all_result_shares = []
            for _ in range(num_participants - 1):
                received_final_share = self.comm.retrieve_private_message(RESULT_SHARE_LABEL)
                final_share_model = jsonpickle.decode(received_final_share, classes=ResultShareMessage)
                all_result_shares.append(final_share_model.share)
            all_result_shares.append(final_result_share)

            # call reconstruct result
            result = reconstruct_secret(all_result_shares)
            # publish final result
            result_message = Message(result)
            self.comm.publish_message(PUBLISH_RESULT_LABEL, result_message.json_rep())

            return result
        else:
            # send final_result_share to leader
            leader = self.get_leader()
            result_share_message = ResultShareMessage(final_result_share)
            self.comm.send_private_message(leader, RESULT_SHARE_LABEL, result_share_message.json_rep())

            # fetch public result
            result_received = self.comm.retrieve_public_message(leader, PUBLISH_RESULT_LABEL)
            result_message = jsonpickle.decode(result_received, classes=Message)
            return result_message.value

    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression,
            shares: Dict[bytes, Share]
    ) -> Share:
        # complex operation
        if isinstance(expr, AddOperation) or isinstance(expr, MultOperation):
            return self.process_expression(expr.left, shares) + self.process_expression(expr.right, shares)
        # secret
        if isinstance(expr, Secret):
            return shares[expr.id]
        # scalar
        return Share(expr.value)

    # Feel free to add as many methods as you want.
