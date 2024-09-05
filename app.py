import streamlit as st
import os
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
import requests
import json
from bs4 import BeautifulSoup
import swagger_client
from swagger_client.rest import ApiException
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.llms import ChatMessage, MessageRole
from openai import OpenAI as OpenAIClient
from subagents import call_agent1, call_agent2, call_agent3, call_agent4 
from prompts import main_agent_prompt,tealeafai_prompt
from llama_index.core import PromptTemplate
from PIL import Image
import nltk
import os

# Set the NLTK data path to a writable directory
nltk.data.path.append("/tmp/nltk_data")

# Download required NLTK data
nltk_data = ["punkt", "stopwords"]
for item in nltk_data:
    try:
        nltk.data.find(f"tokenizers/{item}")
    except LookupError:
        nltk.download(item, download_dir="/tmp/nltk_data")

# API keys
serper_api_key = st.secrets["SERP_API_KEY"]
browserless_api_key = st.secrets["BROWSERLESS_API_KEY"]
news_api = st.secrets["NEWS_API_KEY"]
weather_api_key = st.secrets["WEATHER_API_KEY"]
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Function definitions for PlaneTea app
def search_news(search_input, language='en', limit=3):
    url = "https://api.thenewsapi.com/v1/news/all"
    params = {
        'search': search_input,
        'api_token': news_api,
        'language': language,
        'limit': limit
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch news', 'status_code': response.status_code}

def realtime_weather(location):
    configuration = swagger_client.Configuration()
    configuration.api_key['key'] = weather_api_key
    api_instance = swagger_client.APIsApi(swagger_client.ApiClient(configuration))
    try:
        api_response = api_instance.realtime_weather(location)
        return api_response
    except ApiException as e:
        return f"Exception when calling APIsApi->Realtime weather: {e}"

def google_search(search_keyword):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": search_keyword})
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.json()

def summarize_text(objective, text):
    client = OpenAIClient(api_key=st.secrets["OPENAI_API_KEY"])
    prompt = f"Objective: {objective}\nText: {text}\n\nSummarize the above text keeping the objective in mind:"
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-16k-0613",
        messages=[
            {"role": "system", "content": "Create a summary according to user's instructions"},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def web_scraping(objective, url):
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    data = {"url": url}
    data_json = json.dumps(data)
    response = requests.post(f"https://chrome.browserless.io/content?token={browserless_api_key}", headers=headers, data=data_json)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        if len(text) > 10000:
            return summarize_text(objective, text)
        else:
            return text
    else:
        return f"HTTP request failed with status code {response.status_code}"

# Function for Plain Tea Insights app
def display_saved_graph(filepath):
    graph_path = filepath
    if os.path.exists(graph_path):
        image = Image.open(graph_path)
        st.image(image, caption="Generated Graph", use_column_width=True)
        return "Graph displayed successfully."
    else:
        return "No graph found to display."

# Streamlit UI
st.set_page_config(page_title="TeaLeaf  AI", page_icon="🍵", layout="wide")

# Sidebar
with st.sidebar:
    st.image("Assets/clipart892779.png", caption="TeaLeaf AI")
    st.markdown("### About Our Chat Apps")
    st.write("""
    This multi-chat application combines two powerful AI assistants:
    1. TeaLeaf AI: Your intelligent tea plantation assistant.
    2. TeaLeaf AI Insights: Advanced analytics and insights for your tea business.
    """)
    st.markdown("### Features")
    st.write("- Real-time weather updates")
    st.write("- Latest news on tea industry")
    st.write("- Expert advice on tea cultivation")
    st.write("- Financial document analysis")
    st.write("- Sales and operations insights")
    st.write("- Data visualization")

# Create tabs
tab1, tab2 = st.tabs(["TeaLeaf AI Assitant", "TeaLeaf AI Insights"])

# Tab 1: PlaneTea Chat
with tab1:
    st.title("TeaLeaf  AI 🍵")
    st.subheader("Your Intelligent Tea Plantation Assistant")

    # Initialize OpenAI for PlaneTea
    llm_planetea = OpenAI(model="gpt-4o", api_key=st.secrets["OPENAI_API_KEY"])

    # Initialize or retrieve ChatMemoryBuffer for PlaneTea
    if 'memory_planetea' not in st.session_state:
        st.session_state.memory_planetea = ChatMemoryBuffer.from_defaults(token_limit=3000)

    # Initialize tools for PlaneTea
    tools_planetea = [
        FunctionTool.from_defaults(fn=google_search),
        FunctionTool.from_defaults(fn=web_scraping),
        FunctionTool.from_defaults(fn=realtime_weather),
        FunctionTool.from_defaults(fn=search_news)
    ]

    tealeafai_prompt_ = PromptTemplate(tealeafai_prompt)

    prompt_dict = {
            "agent_worker:system_prompt" : tealeafai_prompt_
        }

    # Initialize ReActAgent for PlaneTea
    agent_planetea = ReActAgent.from_tools(tools_planetea, llm=llm_planetea, memory=st.session_state.memory_planetea, verbose=True)

    agent_planetea.update_prompts(prompt_dict)

    # Initialize chat history for PlaneTea
    if "messages_planetea" not in st.session_state:
        st.session_state.messages_planetea = []

    # Create a container for chat history
    chat_container = st.container()

    # Create a container for the input box at the bottom
    input_container = st.container()

    # Display chat messages for PlaneTea
    with chat_container:
        for message in st.session_state.messages_planetea:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input for PlaneTea
    with input_container:
        prompt_planetea = st.chat_input("How can I assist you with your tea plantation today?")
    
    if prompt_planetea:
        st.session_state.messages_planetea.append({"role": "user", "content": prompt_planetea})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt_planetea)
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                with st.spinner("Thinking..."):
                    response_planetea = agent_planetea.chat(prompt_planetea)
                    full_response = str(response_planetea)
                    message_placeholder.markdown(full_response)
        
        st.session_state.messages_planetea.append({"role": "assistant", "content": full_response})
        st.session_state.memory_planetea.put(ChatMessage(role=MessageRole.USER, content=prompt_planetea))
        st.session_state.memory_planetea.put(ChatMessage(role=MessageRole.ASSISTANT, content=full_response))
        
        st.rerun()

# Tab 2: Plain Tea Insights
with tab2:
    st.title("TeaLeaf AI-Insights")

    # Initialize OpenAI client for Plain Tea Insights
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], default_headers={"OpenAI-Beta": "assistants=v2"})

    main_agent_prompt = PromptTemplate(main_agent_prompt)

    prompt_dict = {
            "agent_worker:system_prompt" : main_agent_prompt
        }

    llm = OpenAI(model="gpt-4o")

    financial_document_agent = FunctionTool.from_defaults(fn=call_agent1)
    sales_and_operations_agent = FunctionTool.from_defaults(fn=call_agent2)
    information_gathering_agent = FunctionTool.from_defaults(fn=call_agent3)
    insight_agent = FunctionTool.from_defaults(fn=call_agent4)
    display_graph = FunctionTool.from_defaults(fn=display_saved_graph)


    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if 'memory' not in st.session_state:
        st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=3000)   

    agent = ReActAgent.from_tools(
        [financial_document_agent, sales_and_operations_agent, information_gathering_agent, insight_agent, display_graph],
        llm=llm,
        memory=st.session_state.memory,
        verbose=True,
        max_iterations=20  # Increase this value, default is usually 5
    )

    agent.update_prompts(prompt_dict)     

    # Create a container for chat history
    chat_container = st.container()

    # Create a container for the input box at the bottom
    input_container = st.container()

    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input at the bottom
    with input_container:
        user_query = st.chat_input("Ask me anything")

    if user_query:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                with st.spinner("Thinking..."):
                    try:
                        response = agent.chat(user_query)
                        # Stream the response
                        for chunk in str(response).split():
                            full_response += chunk + " "
                            message_placeholder.markdown(full_response + "▌")
                        message_placeholder.markdown(full_response)
                    except ValueError as e:
                        error_message = "I apologize, but I'm having trouble processing your request. Could you please rephrase or simplify your question?"
                        message_placeholder.markdown(error_message)
                        full_response = error_message

        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

        # Update memory
        st.session_state.memory.put(ChatMessage(role=MessageRole.USER, content=user_query))
        st.session_state.memory.put(ChatMessage(role=MessageRole.ASSISTANT, content=full_response))

        # Display graph if generated
        if "Graph saved successfully" in full_response:
            graph_path = full_response.split("at ")[-1].strip()
            display_saved_graph(graph_path)

        # st.rerun()

# # Footer
# st.markdown("---")
# st.markdown("Powered by LlamaIndex and OpenAI")