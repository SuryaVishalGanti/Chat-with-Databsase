import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

# Set up the Streamlit page
st.set_page_config(page_title="Surya's Langchain: Chat with Employees Data")
st.title("Surya's Langchain Chatbot: Chat with Employees Data")

# Define database options
localdb = "use_localdb"
mysql = "use_mysql"

radio_opt = ["Use SQLite 3 with my Database", "Connect to MySQL Database"]
selected_opt = st.sidebar.radio(label="Choose the DB to chat with", options=radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_uri = mysql
    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
else:
    db_uri = localdb

# Get API key
api_key = st.sidebar.text_input(label="Groq API key", type="password")

# Check required inputs
if not db_uri:
    st.info("Please enter the database information.")
    st.stop()

if not api_key:
    st.info("Please add your Groq API Key.")
    st.stop()

# Initialize LLM model
llm = ChatGroq(groq_api_key=api_key, model="qwen-2.5-coder-32b", streaming=True)

# Function to configure the database
@st.cache_resource(ttl=7200)
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == localdb:
        dbfilepath = Path("employee1.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri == mysql:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

# Configure DB connection
if db_uri == mysql:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)

# Initialize the agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# Store chat messages in session state
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
user_query = st.chat_input(placeholder="Ask anything from the Database")

if "user_query" not in st.session_state:
    st.session_state["user_query"] = ""

# Create two columns: one for input and one for reload button
col1, col2 = st.columns([4, 1])

with col1:
    user_query = st.text_input("Ask anything from the Database", value=st.session_state["user_query"])

# Process the user input
if user_query:
    st.session_state["messages"].append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.write(response)