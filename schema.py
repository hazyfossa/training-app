from enum import Enum
from graphene import Enum as GrapheneEnum

from tinydb import TinyDB, where
from tinydb.operations import add, subtract
from tinydb.table import Document

from graphene import (
    ID,
    Field,
    Float,
    Int,
    List,
    Mutation,
    ObjectType,
    Schema,
    String,
    Boolean,
)
from graphene.types.objecttype import ObjectTypeMeta

from scalars import Email, Phone

# Database

_db, db = TinyDB("./db.json"), {}

for table in ["gyms", "trainings", "customers", "purchases"]:
    db[table] = _db.table(table)


class TinyDBObject(ObjectType):
    id = ID(required=True)

    def resolve_id(parent, info):
        return parent.doc_id


# Gym


class Gym(TinyDBObject):
    id = ID(required=True)
    name = String(required=True)
    admin_name = String(required=True)
    admin_phone = Phone(required=True)
    trainings = List(lambda: Training(), required=True)
    free_slots = Int(required=True)

    def resolve_trainings(parent, info):
        return [db["trainings"].get(doc_id=id) for id in parent["trainings"]]


class CreateGym(Mutation):
    Output = Gym

    class Arguments:
        name = String(required=True)
        admin_name = String(required=True)
        admin_phone = Phone(required=True)
        trainings = List(ID, required=True, default_value=[])
        free_slots = Int(required=True)

    def mutate(parent, info, **gym):
        id = db["gyms"].insert(gym)
        return Document(gym, id)


class UpdateGym(Mutation):
    Output = Gym

    class Arguments:
        id = ID(required=True)
        name = String()
        admin_name = String()
        admin_phone = Phone()
        trainings = List(ID)
        free_slots = Int()

    def mutate(parent, info, id, **gym):
        db["gyms"].update(gym, doc_ids=[int(id)])
        return db["gyms"].get(doc_id=id)


# Training


class TrainingType(str, Enum):
    INDIVIDUAL = "i"
    GROUP = "g"
    WITH_TRAINER = "t"


TrainingType = GrapheneEnum.from_enum(
    TrainingType, description="Stored in DB as strings"
)


class Training(TinyDBObject):
    type = TrainingType(required=True)
    price = Float(required=True)
    gym = Field(Gym(), required=True)

    def resolve_gym(parent, info):
        return db["gyms"].get(doc_id=parent["gym"])


class CreateTraining(Mutation):
    Output = Training

    class Arguments:
        type = TrainingType(required=True)
        price = Int(required=True)
        gym = ID(required=True)

    def mutate(parent, info, **training):
        id = db["trainings"].insert(training)
        return Document(training, id)


class UpdateTraining(Mutation):
    Output = Training

    class Arguments:
        id = ID(required=True)
        type = TrainingType()
        price = Int()
        gym = ID()

    def mutate(parent, info, id, **training):
        id = db["trainings"].update(training, doc_ids=[id])
        return db["trainings"].get(doc_id=id)


# Customer


class Customer(TinyDBObject):
    name = String(required=True)
    email = Email(required=True)
    register = List(Training, required=True)


class CreateCustomer(Mutation):
    Output = Customer

    class Arguments:
        name = String(required=True)
        email = Email(required=True)
        register = List(ID, required=True, default_value=[])

    def mutate(parent, info, **customer):
        id = db["customers"].insert(customer)
        return Document(customer, id)


class UpdateCustomer(Mutation):
    Output = Customer

    class Arguments:
        id = ID(required=True)
        name = String()
        email = Email()
        register = List(ID)

    def mutate(parent, info, id, **customer):
        db["customers"].update(customer, doc_ids=[id])
        return db["customers"].get(doc_id=id)


# Purchase


class Purchase(TinyDBObject):
    training = Field(Training(), required=True)
    customer = Field(Customer(), required=True)
    price = Float(required=True)
    income = Float(required=True)

    def resolve_price(parent, info):
        return db["trainings"].get(doc_id=parent["training"])["price"]


class MakePurchase(Mutation):
    class Arguments:
        customerId = ID(required=True)
        trainingId = ID(required=True)

    training = Field(Training())
    customer = Field(Customer())
    purchase = Field(Purchase())

    def mutate(parent, info, customerId, trainingId):
        training = db["trainings"].get(doc_id=trainingId)

        gymId = training["gym"]
        db["gyms"].update(subtract("free_slots", 1), doc_ids=[int(gymId)])

        purchase = {
            "training": trainingId,
            "customer": customerId,
            "income": training["price"] * 0.8,
        }

        db["customers"].update(add("register", trainingId), doc_ids=[int(customerId)])
        customer = db["customers"].get(doc_id=customerId)

        purchaseId = db["purchases"].insert(purchase)
        return MakePurchase(training, customer, Document(purchase, purchaseId))


# Deletion


class SchemaObject(GrapheneEnum):
    Gym = "gyms"
    Customer = "customers"
    Training = "trainings"


class Delete(Mutation):
    class Arguments:
        id = ID(required=True)
        object = SchemaObject(required=True)

    ok = Boolean(required=True)

    def mutate(parent, info, id, object):
        db[object.value].remove(doc_ids=[int(id)])
        return Delete(True)


# Query


def query_db(name, *_, id):
    return db[name + "s"].get(doc_id=id)


class Query(ObjectType):
    class Meta:
        default_resolver = query_db

    gym = Field(Gym, id=ID(required=True))
    training = Field(Training, id=ID(required=True))
    customer = Field(Customer, id=ID(required=True))

    all_trainings = List(Training, required=True)
    all_gyms = List(Gym, required=True)

    purchases = Field(List(Purchase, required=True), customerID=ID(required=True))

    def resolve_all_trainings(root, info):
        return db["trainings"].all()

    def resolve_all_gyms(root, info):
        return db["gyms"].all()

    def resolve_purchases(root, info, id):
        return db["purchases"].search(where("customer") == id)


# Mutation


def compose_mutations(mutations):
    mutation = {}

    for graphql_mutation in mutations:
        name = graphql_mutation.__name__
        mutation[name] = graphql_mutation.Field()

    return ObjectTypeMeta("Mutation", (ObjectType,), mutation)


mutation_class = compose_mutations(
    [
        CreateGym,
        UpdateGym,
        CreateTraining,
        UpdateTraining,
        CreateCustomer,
        UpdateCustomer,
        MakePurchase,
        Delete,
    ]
)


schema = Schema(query=Query, mutation=mutation_class)
