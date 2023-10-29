from re import match

from graphql import GraphQLError
from graphql.language import ast

from config import config
from graphene import Scalar, String


class ValidatedScalar(Scalar):
    data_type = None
    regex = NotImplemented

    @classmethod
    def validate(self, value):
        if not match(self.regex, value):
            raise GraphQLError(f"Invalid {self.data_type}!")
        return value

    @classmethod
    def parse_value(self, value):
        return self.validate(value)

    @staticmethod
    def serialize(value):
        return value

    @classmethod
    def parse_literal(self, node, _variables=None):
        if isinstance(node, ast.StringValueNode):
            return self.validate(node.value)


if config["validate_email"]:

    class Email(ValidatedScalar):
        data_type = "email"
        regex = config["email_regex"]

else:

    class Email(String):
        pass


if config["validate_phone"]:

    class Phone(ValidatedScalar):
        data_type = "phone number"
        regex = config["phone_regex"]

else:

    class Phone(String):
        pass
