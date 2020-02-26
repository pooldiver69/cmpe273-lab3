from ariadne import QueryType, MutationType, graphql_sync, make_executable_schema
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify

type_defs = """
    type Query {
        students(id: ID!): printStudent!
    }

    type Mutation {
        addStudent(input: student!, id: ID!): Boolean
        createClass(input: class!, id: ID!): Boolean
    }

    input student {
        name: String!
    } 

    input class {
        name: String!
        students!: student!
    }

    type printStudent {
        name: String!
    }


"""

students = {}

query = QueryType()

@query.field("students")
def resolve_getStudent(_, info, id):
    return students[id]


mutation = MutationType()
@mutation.field('addStudent')
def resolve_addStudent(_, info, input, id):
    print(input)
    students[id] = input
    return True

schema = make_executable_schema(type_defs, [query, mutation])

app = Flask(__name__)


@app.route("/graphql", methods=["GET"])
def graphql_playgroud():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(debug=True)