# external imports
from google.protobuf.reflection import GeneratedProtocolMessageType

# syft imports
import syft as sy
from ..common.uid import UID
from ..common.pointer import AbstractPointer
from ..node.abstract.node import AbstractNode
from ..common.serde.deserialize import _deserialize
from ...decorators.syft_decorator_impl import syft_decorator
from ..node.common.action.get_object_action import GetObjectAction
from ...proto.core.pointer.pointer_pb2 import Pointer as Pointer_PB


class Pointer(AbstractPointer):

    # automatically generated subclasses of Pointer need to be able to look up
    # the path and name of the object type they point to as a part of serde
    path_and_name: str

    def __init__(self, location, id_at_location=None):
        if id_at_location is None:
            id_at_location = UID()

        self.location = location
        self.id_at_location = id_at_location

    def get(self):
        obj_msg = GetObjectAction(
            obj_id=self.id_at_location,
            address=self.location.address,
            reply_to=self.location.address,
        )
        response = self.location.send_immediate_msg_with_reply(msg=obj_msg)

        return response.obj

    @syft_decorator(typechecking=True)
    def _object2proto(self) -> Pointer_PB:
        """Returns a protobuf serialization of self.

        As a requirement of all objects which inherit from Serializable,
        this method transforms the current object into the corresponding
        Protobuf object so that it can be further serialized.

        :return: returns a protobuf object
        :rtype: Pointer_PB

        .. note::
            This method is purely an internal method. Please use object.serialize() or one of
            the other public serialization methods if you wish to serialize an
            object.
        """
        return Pointer_PB(
            points_to_object_with_path=self.path_and_name,
            pointer_name=type(self).__name__,
            id_at_location=self.id_at_location.serialize(),
            location=self.location.address.serialize(),
        )

    @staticmethod
    def _proto2object(proto: Pointer_PB) -> "Pointer":
        """Creates a Pointer from a protobuf

        As a requirement of all objects which inherit from Serializable,
        this method transforms a protobuf object into an instance of this class.

        :return: returns an instance of Pointer
        :rtype: Pointer

        .. note::
            This method is purely an internal method. Please use syft.deserialize()
            if you wish to deserialize an object.
        """
        points_to_type = sy.lib_ast(
            proto.points_to_object_with_path, return_callable=True
        )
        pointer_type = getattr(points_to_type, proto.pointer_name)
        return pointer_type(
            id_at_location=_deserialize(blob=proto.id_at_location),
            location=_deserialize(blob=proto.location),
        )

    @staticmethod
    def get_protobuf_schema() -> GeneratedProtocolMessageType:
        """ Return the type of protobuf object which stores a class of this type

        As a part of serializatoin and deserialization, we need the ability to
        lookup the protobuf object type directly from the object type. This
        static method allows us to do this.

        Importantly, this method is also used to create the reverse lookup ability within
        the metaclass of Serializable. In the metaclass, it calls this method and then
        it takes whatever type is returned from this method and adds an attribute to it
        with the type of this class attached to it. See the MetaSerializable class for details.

        :return: the type of protobuf object which corresponds to this class.
        :rtype: GeneratedProtocolMessageType

        """

        return Pointer_PB

    def request_access(
        self, node: AbstractNode, request_name: str = "", request_description: str = "",
    ) -> None:
        from ..node.domain.service import RequestMessage

        msg = RequestMessage(
            request_name=request_name,
            request_description=request_description,
            address=self.location,
            owner_address=node.domain,  # type: ignore
            object_id=self.id_at_location,
        )

        self.location.send_immediate_msg_without_reply(msg=msg)

        node.requests.register_mapping(self.id_at_location, msg.request_id)  # type: ignore

    def check_access(self, node: AbstractNode, request_id: UID) -> any:  # type: ignore
        from ..node.domain.service import (
            RequestAnswerMessage,
            RequestAnswerResponseService,
        )

        msg = RequestAnswerMessage(
            request_id=request_id, address=self.location, reply_to=node.domain  # type: ignore
        )
        response = self.location.send_immediate_msg_with_reply(msg=msg)

        # this should be handled by the service by default, should be patched after 0.3.0
        RequestAnswerResponseService.process(node, response)

        return response.status