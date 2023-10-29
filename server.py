import uvicorn
from starlette.applications import Starlette
from starlette_graphene3 import GraphQLApp, make_playground_handler

from config import config
from schema import schema

app = Starlette()
app.mount("/", GraphQLApp(schema, on_get=make_playground_handler()))


if __name__ == "__main__":
    uvicorn.run(app, host=config["host"], port=config["port"])
