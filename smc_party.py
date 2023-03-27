"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
from typing import (
    Dict, List
)

from communication import Communication
from expression import (
    Expression,
    Secret,
    Scalar,
    AddOperation,
    MultOperation,
    collect_secret_ids
)
from message_utils import ShareMessage, SECRET_SHARE_LABEL, RESULT_SHARE_LABEL, ResultShareMessage, Message, \
    PUBLISH_RESULT_LABEL, BEAVER_CONST_SHARE_LABEL, BeaverConstShareMessage, BEAVER_CONST_RESULT_LABEL, \
    BeaverConstResultMessage
from protocol import ProtocolSpec
from secret_sharing import (
    share_secret, Share, Constant, reconstruct_secret, FIELD_MODULUS, )
from timeit import default_timer as timer

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
        # each party has sorted list of all participants in the protocol
        self.protocol_spec.participant_ids.sort()
        self.num_participants = len(self.protocol_spec.participant_ids)
        self.value_dict = value_dict
        self.bytes_consumed = 0
        self.time_consumed = 0

    def is_leader(self) -> bool:
        """ Should the party do the operations that are done by one party exclusively. """
        return self.client_id == self.protocol_spec.participant_ids[0]

    def get_leader(self) -> str:
        """ Returns the leader client id. """
        return self.protocol_spec.participant_ids[0]

    def is_self(self, participant: str) -> bool:
        """ Is the current party the one with the provided client id. """
        return self.client_id == participant

    def get_other_participants_list(self) -> List[str]:
        """ Returns list of client ids of the other participants in the protocol. """
        return [participant for participant in self.protocol_spec.participant_ids if participant != self.client_id]

    def get_personal_shares(self) -> Dict[bytes, list[Share]]:
        """ Returns dict of personal secret ids as keys and list of shares as values. """
        return {secret.id: share_secret(value, self.num_participants) for secret, value in self.value_dict.items()}

    def disseminate_personal_shares(self, personal_shares: Dict[bytes, list[Share]]) -> Dict[bytes, Share]:
        """ Disseminates shares of personal secrets to the other participants in the protocol. """
        shares_dict = {}
        for i in range(self.num_participants):
            for (id, shares) in personal_shares.items():
                if self.is_self(self.protocol_spec.participant_ids[i]):
                    shares_dict[id] = shares[i]
                else:
                    self.send_secret_share(ShareMessage(id, shares[i]), self.protocol_spec.participant_ids[i])
        return shares_dict

    def collect_secret_ids_other_parties(self):
        """ Returns ids of all secrets in the expression except for the personal ones. """
        personal_secret_ids = [secret.id for secret in self.value_dict.keys()]
        all_secret_ids = collect_secret_ids(self.protocol_spec.expr)
        return [secret_id for secret_id in all_secret_ids if secret_id not in personal_secret_ids]

    def send_secret_share(self, share: ShareMessage, destination: str):
        """ Sends a share to the provided destination. """
        self.comm.send_private_message(destination, SECRET_SHARE_LABEL + share.id, share.serialize())

    def retrieve_secret_share(self, secret_id: str) -> ShareMessage:
        """ Retrieves a share for the provided secret id. """
        msg = self.comm.retrieve_private_message(SECRET_SHARE_LABEL + secret_id)
        self.bytes_consumed += len(msg)
        return ShareMessage.deserialize(msg)

    def send_result_share(self, share: ResultShareMessage, destination: str):
        """ Sends a share of the final result to the provided destination. """
        self.comm.send_private_message(destination, RESULT_SHARE_LABEL + self.client_id, share.serialize())

    def retrieve_result_share(self, participant: str) -> ResultShareMessage:
        """ Retrieves a share of the final result from the provided participant. """
        msg = self.comm.retrieve_private_message(RESULT_SHARE_LABEL + participant)
        self.bytes_consumed += len(msg)
        return ResultShareMessage.deserialize(msg)

    def publish_final_result(self, message: Message):
        """ Sends the final result as public message. """
        self.comm.publish_message(PUBLISH_RESULT_LABEL, message.serialize())

    def retrieve_final_result(self, sender: str) -> Message:
        """ Retrieves the final result from the provided participant. """
        msg = self.comm.retrieve_public_message(sender, PUBLISH_RESULT_LABEL)
        self.bytes_consumed += len(msg)
        return Message.deserialize(msg)

    def send_beaver_const_share(self, share: BeaverConstShareMessage, op_id: str, destination: str):
        """ Sends shares of beaver constants for the provided operation id to the provided destination. """
        self.comm.send_private_message(destination, BEAVER_CONST_SHARE_LABEL + op_id + "_" + self.client_id,
                                       share.serialize())

    def retrieve_beaver_const_share(self, op_id: str, participant: str) -> BeaverConstShareMessage:
        """ Retrieves shares of beaver constants for the provided operation id from the provided participant. """
        msg = self.comm.retrieve_private_message(BEAVER_CONST_SHARE_LABEL + op_id + "_" + participant)
        self.bytes_consumed += len(msg)
        return BeaverConstShareMessage.deserialize(msg)

    def publish_beaver_const_result(self, message: BeaverConstResultMessage, op_id: str):
        """ Sends the final beaver constants for the provided operation id as public message. """
        self.comm.publish_message(BEAVER_CONST_RESULT_LABEL + op_id, message.serialize())

    def retrieve_beaver_const_result(self, sender: str, op_id: str) -> BeaverConstResultMessage:
        """ Retrieves the final beaver constants for the provided operation id from the provided participant. """
        msg = self.comm.retrieve_public_message(sender, BEAVER_CONST_RESULT_LABEL + op_id)
        self.bytes_consumed += len(msg)
        return BeaverConstResultMessage.deserialize(msg)

    def retrieve_beaver_triplets(self, op_id: str):
        """ Retrieves the shares of beaver triplets for the provided operation id. """
        triplets = self.comm.retrieve_beaver_triplet_shares(op_id)
        self.bytes_consumed += triplets.__sizeof__()
        return triplets

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        start = timer()
        expression = self.protocol_spec.expr
        personal_shares = self.get_personal_shares()
        # send personal shares and create map of secret Share(s) per ID
        shares_dict = self.disseminate_personal_shares(personal_shares)

        secret_ids_to_receive = self.collect_secret_ids_other_parties()
        for sid in secret_ids_to_receive:
            secret_share = self.retrieve_secret_share(sid.decode())
            shares_dict[secret_share.id.encode()] = secret_share.share

        # process locally
        final_result_share = self.process_expression(expression, shares_dict)

        # edge case where the expression to be computed consists of scalars only.
        # every party will have the same result share, so we can just return it.
        if isinstance(final_result_share, Constant):

            end = timer()
            self.time_consumed = end - start
            return final_result_share.value

        # protocol phase one
        all_result_shares = [final_result_share]
        if not self.is_leader():
            self.send_result_share(ResultShareMessage(final_result_share), self.get_leader())
        else:
            other_participants = self.get_other_participants_list()
            for participant in other_participants:
                all_result_shares.append(self.retrieve_result_share(participant).share)

        # protocol phase two
        if self.is_leader():
            result = reconstruct_secret(all_result_shares)
            self.publish_final_result(Message(result))

            end = timer()
            self.time_consumed = end - start
            return result
        else:
            result_deserialized = self.retrieve_final_result(self.get_leader())

            end = timer()
            self.time_consumed = end - start
            return result_deserialized.value

    # Suggestion: To process expressions, make use of the *visitor pattern* like so:
    def process_expression(
            self,
            expr: Expression,
            shares: Dict[bytes, Share]
    ):
        """
        Processes an expression and returns party's share. Possibly includes communication in case of multiplication of
        secrets.
        """
        # Complex operation
        if isinstance(expr, AddOperation):
            left_addend = self.process_expression(expr.left, shares)
            right_addend = self.process_expression(expr.right, shares)
            if isinstance(left_addend, Share) and isinstance(right_addend, Constant):
                if self.is_leader():
                    return left_addend + right_addend
                else:
                    return left_addend
            elif isinstance(left_addend, Constant) and isinstance(right_addend, Share):
                if self.is_leader():
                    return left_addend + right_addend
                else:
                    return right_addend
            else:
                return left_addend + right_addend
        elif isinstance(expr, MultOperation):
            left_multiplier = self.process_expression(expr.left, shares)
            right_multiplier = self.process_expression(expr.right, shares)
            if isinstance(left_multiplier, Share) and isinstance(right_multiplier, Share):
                # use beaver triplets
                op_id = expr.id.decode()
                other_participants = self.get_other_participants_list()
                (a_share, b_share, c_share) = self.retrieve_beaver_triplets(op_id)
                x_const_share = left_multiplier - a_share
                y_const_share = right_multiplier - b_share

                # exchange beaver constant shares
                all_x_const_shares = [x_const_share]
                all_y_const_shares = [y_const_share]
                if not self.is_leader():
                    self.send_beaver_const_share(BeaverConstShareMessage(x_const_share, y_const_share), op_id,
                                                 self.get_leader())
                else:
                    for participant in other_participants:
                        beaver_const_share = self.retrieve_beaver_const_share(op_id, participant)
                        all_x_const_shares.append(beaver_const_share.x_part)
                        all_y_const_shares.append(beaver_const_share.y_part)

                # exchange final beaver constants
                if self.is_leader():
                    x_const = reconstruct_secret(all_x_const_shares)
                    y_const = reconstruct_secret(all_y_const_shares)
                    self.publish_beaver_const_result(BeaverConstResultMessage(x_const, y_const), op_id)
                else:
                    result_deserialized = self.retrieve_beaver_const_result(self.get_leader(), op_id)
                    x_const = result_deserialized.x_part
                    y_const = result_deserialized.y_part

                # compute and return share
                return self.compute_secret_multiplication_share(left_multiplier, right_multiplier, c_share, x_const,
                                                                y_const)
            else:
                return left_multiplier * right_multiplier
        # Secret
        elif isinstance(expr, Secret):
            return shares[expr.id]
        # Scalar
        elif isinstance(expr, Scalar):
            return Constant(expr.value)
        else:
            raise ValueError("Unsupported expression type")

    def compute_secret_multiplication_share(self, left_multiplier: Share, right_multiplier: Share, c_share: Share,
                                            x_const: int, y_const: int):
        """
        Locally computes the final share of the secret multiplication.
        """
        base_value = (((c_share.value + ((left_multiplier.value * y_const) % FIELD_MODULUS)) % FIELD_MODULUS) + (
                (right_multiplier.value * x_const) % FIELD_MODULUS)) % FIELD_MODULUS
        if self.is_leader():
            return Share((base_value - ((x_const * y_const) % FIELD_MODULUS)) % FIELD_MODULUS)
        else:
            return Share(base_value)
