"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
import time
from typing import (
    Dict
)

from communication import Communication
from expression import (
    Expression,
    Secret, collect_secret_ids, AddOperation, MultOperation
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
        self.protocol_spec.participant_ids.sort()
        self.num_participants = len(self.protocol_spec.participant_ids)
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

    def get_other_participants_list(self):
        return [participant for participant in self.protocol_spec.participant_ids if participant != self.client_id]

    def get_personal_shares(self) -> Dict[bytes, list[Share]]:
        return {secret.id: share_secret(value, self.num_participants) for secret, value in self.value_dict.items()}

    def disseminate_personal_shares(self, personal_shares: Dict[bytes, list[Share]]) -> Dict[bytes, Share]:
        shares_dict = {}
        for i in range(self.num_participants):
            for (id, shares) in personal_shares.items():
                if self.is_self(self.protocol_spec.participant_ids[i]):
                    shares_dict[id] = shares[i]
                else:
                    self.send_secret_share(ShareMessage(id, shares[i]), self.protocol_spec.participant_ids[i])
        return shares_dict

    def collect_secret_ids_other_parties(self):
        personal_secret_ids = [secret.id for secret in self.value_dict.keys()]
        all_secret_ids = collect_secret_ids(self.protocol_spec.expr)
        return [secret_id for secret_id in all_secret_ids if secret_id not in personal_secret_ids]

    def send_secret_share(self, share: ShareMessage, destination: str):
        self.comm.send_private_message(destination, SECRET_SHARE_LABEL + share.id, share.serialize())

    def retrieve_secret_share(self, secret_id: str) -> ShareMessage:
        return ShareMessage.deserialize(self.comm.retrieve_private_message(SECRET_SHARE_LABEL + secret_id))

    def send_result_share(self, share: ResultShareMessage, destination: str):
        self.comm.send_private_message(destination, RESULT_SHARE_LABEL + self.client_id, share.serialize())

    def retrieve_result_share(self, participant: str) -> ResultShareMessage:
        return ResultShareMessage.deserialize(self.comm.retrieve_private_message(RESULT_SHARE_LABEL + participant))

    def publish_final_result(self, message: Message):
        self.comm.publish_message(PUBLISH_RESULT_LABEL, message.serialize())

    def retrieve_final_result(self, sender: str) -> Message:
        return Message.deserialize(self.comm.retrieve_public_message(sender, PUBLISH_RESULT_LABEL))

    def compute_delay_in_seconds(self):
        return self.num_participants - 1

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        expression = self.protocol_spec.expr

        # share secrets that belong to this client
        personal_shares = self.get_personal_shares()
        # send personal shares and create map of secret Share(s) per ID
        shares_dict = self.disseminate_personal_shares(personal_shares)

        secret_ids_to_receive = self.collect_secret_ids_other_parties()
        for sid in secret_ids_to_receive:
            secret_share = self.retrieve_secret_share(sid.decode())
            shares_dict[secret_share.id.encode()] = secret_share.share

        # process locally
        final_result_share = self.process_expression(expression, shares_dict)
        print(self.client_id + " result share: " + str(final_result_share))

        # protocol phase one
        all_result_shares = [final_result_share]
        if not self.is_leader():
            # send final_result_share to leader
            self.send_result_share(ResultShareMessage(final_result_share), self.get_leader())
            time.sleep(self.compute_delay_in_seconds())
        else:
            # wait for remaining final_result_share(s)
            other_participants = self.get_other_participants_list()
            time.sleep(self.compute_delay_in_seconds())
            for participant in other_participants:
                all_result_shares.append(self.retrieve_result_share(participant).share)
            print("leader has: " + str(all_result_shares))

        # protocol phase two
        if self.is_leader():
            # reconstruct and publish result
            result = reconstruct_secret(all_result_shares)
            self.publish_final_result(Message(result))

            return result
        else:
            time.sleep(self.compute_delay_in_seconds())
            # fetch public result
            result_deserialized = self.retrieve_final_result(self.get_leader())
            print(self.client_id + " receives from leader " + str(result_deserialized))

            return result_deserialized.value

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
