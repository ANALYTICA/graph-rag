import time
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from graphRAG import get_retriever, get_model, rag_question
from vectorize import vectorize_documents
from link_chunks import link_chunks
from create_relationships import build_relationships
from create_documents import build_documents
#from llama import load_model
#from data_chat import get_crc

#model = load_model()



def textbox(text, box="other"):
    style = {
        "max-width": "55%",
        "width": "max-content",
        "padding": "10px 15px",
        "border-radius": "25px",
    }

    if box == "self":
        style["margin-left"] = "auto"
        style["margin-right"] = 0

        color = "primary"
        inverse = True

    elif box == "other":
        style["margin-left"] = 0
        style["margin-right"] = "auto"

        color = "light"
        inverse = False

    else:
        raise ValueError("Incorrect option for `box`.")

    return dbc.Card(text, style=style, body=True, color=color, inverse=inverse)


conversation = html.Div(
    style={
        "width": "80%",
        "max-width": "800px",
        "height": "70vh",
        "margin": "auto",
        "overflow-y": "auto",
    },
    id="display-conversation",
)

controls = dbc.InputGroup(
    style={"width": "80%", "max-width": "800px", "margin": "auto"},
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        dbc.Button("Submit", id="submit"),
    ],
)


# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server


# Define Layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H1("Chat with your data . . . "),
        html.Hr(),
        #dcc.Store(id="store-conversation", data=""),
        dcc.Store(id="store-conversation", data=[]),
        conversation,
        controls,
    ],
)


@app.callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(x, box="self") if i % 2 == 0 else textbox(x, box="other")
        for i, x in enumerate(chat_history)
    ]
retriever = get_retriever()
llm = get_model()
build_documents()
vectorize_documents()
link_chunks()
build_relationships()

@app.callback(
    [Output("store-conversation", "data"), Output("user-input", "value")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data")],
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    
    print("n_clicks: ", n_clicks)
    print("n_submit: ", n_submit)
    print("user_input: ", user_input)
    print("chat_history: ", chat_history, " ", len(chat_history))

    if n_clicks == 0:
        return "", ""

    if user_input is None or user_input == "":
        return chat_history, ""
    response = rag_question(user_input, llm, retriever)["result"]
    if len(chat_history) == 0:
        chat_history = [user_input, response]
    else:
        chat_history = chat_history + [user_input]
        chat_history = chat_history + [response]
    return chat_history, ""


if __name__ == "__main__":
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0', port=8050, debug=False)
