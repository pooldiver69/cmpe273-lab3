from ariadne import QueryType, MutationType, graphql_sync, make_executable_schema
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify

type_defs = """
    type Query {
        students(id: ID!): printStudent!
        classes(id: ID!): printClass!
    }

    type Mutation {
        createStudent(input: student!, id: ID!): Boolean
        createClass(input: class!, id: ID!): Boolean
        addStudentToclass(student_id: ID!, class_id: ID!): Boolean
    }

    input student {
        name: String!
    } 

    input class {
        name: String!
    }

    type printStudent {
        name: String!
    }

    type printClass {
        name: String!
        students: [printStudent]!
    }
"""

students = {}
classes = {}

query = QueryType()

@query.field("students")
def resolve_students(_, info, id):
    return students[id]
    
@query.field("classes")
def resolve_classes(_, info, id):
    return classes[id]

mutation = MutationType()
@mutation.field('createStudent')
def resolve_createStudent(_, info, input, id):
    # print(input)
    students[id] = input
    return True

@mutation.field('createClass')
def resolve_createClass(_, info, input, id):
    input['students'] = []
    classes[id] = input
    return True

@mutation.field('addStudentToclass')
def resolve_addStudentToclass(_, info, student_id, class_id):
    classes[class_id]['students'].append(students[student_id])
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