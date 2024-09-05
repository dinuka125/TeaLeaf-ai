from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import  FunctionTool 
import os
from dotenv import load_dotenv
from prompts import agent_1_prompt, agent_2_prompt, agent_3_prompt,agent_4_prompt
from llama_index.core import(
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    PromptTemplate

)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core import VectorStoreIndex
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from apicall import call_sales_api, call_operations_api, call_dashboard_api
from apicall import search_news, google_search, web_scraping, realtime_weather,load_tea_stock_data
from llama_index.agent.openai import OpenAIAgent
from llama_index.tools.code_interpreter.base import CodeInterpreterToolSpec
import streamlit as st 


load_dotenv()
OpenAI.api_key= st.secrets["OPENAI_API_KEY"]
os.environ["LLAMA_CLOUD_API_KEY"] = st.secrets["LLAMA_CLOUD_API_KEY"]



def call_agent1(instructions):
    """
        Agent 1/ Financial_document_agent
        This Agent responsible for Financial documents and financial information about the 
        Sub Tea plantation companies operating under main Tea company.
        It will provide you, past financial data and other financial info.
    """

    print("====== Executing agent1 ======")

    agent1_prompt = PromptTemplate(agent_1_prompt)

    prompt_dict = {
        "agent_worker:system_prompt" : agent1_prompt
    }

    llm = OpenAI(model="gpt-4o")

    try:
        storage_context = StorageContext.from_defaults(
            persist_dir="./storage/Tea_plantations_maskeliya"
        )
        maskeliay_plantation_index = load_index_from_storage(storage_context)

        storage_context = StorageContext.from_defaults(
            persist_dir="./storage/Tea_plantations_talawakele"
        )
        talawakele_plantation_index = load_index_from_storage(storage_context)

        index_loaded = True
    except:
        index_loaded = False

    if not index_loaded:
        plantation_docs_1 = SimpleDirectoryReader(
            input_files=["files/723_1693476523167.pdf"]
        ).load_data()

        maskeliay_plantation_index = VectorStoreIndex.from_documents(plantation_docs_1)

        maskeliay_plantation_index.storage_context.persist(persist_dir="./storage/Tea_plantations_maskeliya")

        plantation_docs_2 = SimpleDirectoryReader(
            input_files=["files/726_1685638811126.pdf"]
        ).load_data()

        talawakele_plantation_index = VectorStoreIndex.from_documents(plantation_docs_2)

        talawakele_plantation_index.storage_context.persist(persist_dir="./storage/Tea_plantations_talawakele")

    maskeliya_plantation_info_engine = maskeliay_plantation_index.as_query_engine(similarity_top_k=3)
    talawakele_plantation_info_engine = talawakele_plantation_index.as_query_engine(similarity_top_k=3)


    query_engine_tools = [
    QueryEngineTool(
        query_engine=maskeliya_plantation_info_engine,
        metadata=ToolMetadata(
            name="Maskeliya_Plantation_financial_info",
            description=(
                "Provides financial information about sub Tea companies - Maskeliya Plantations"
                "Use a detailed plain text question as input to the tool"
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=talawakele_plantation_info_engine,
        metadata=ToolMetadata(
            name="Talawakele_Plantation_financial_info",
            description=(
                "Provides financial information about sub Tea companies - Talawakele Plantations"
                "Use a detailed plain text question as input to the tool"
            ),
        ),
    )    
    ]

    agent = ReActAgent.from_tools(query_engine_tools, llm=llm, verbose=True)

    agent.update_prompts(prompt_dict)

    response = agent.chat(instructions)
    response = str(response)
    print(response)

    print("====== Executed agent1 ======")


    return (response)


def call_agent2(instructions):
    """
    Agent 2/ Sales_and_operations agent
    This Agent responsible for sales / tea stock / and operational information about the Sub Tea plantation companies operating under main Tea company.
    You can get current operational info from this agent
    
    """
    print("====== Executing agent2 ======")


    agent_3 = PromptTemplate(agent_2_prompt)

    prompt_dict = {
        "agent_worker:system_prompt" : agent_3
    }

    llm = OpenAI(model="gpt-4o")

    call_sales_api_ = FunctionTool.from_defaults(fn=call_sales_api)
    call_operations_api_ = FunctionTool.from_defaults(fn=call_operations_api)
    call_dashboard_api_ = FunctionTool.from_defaults(fn=call_dashboard_api)
    get_tea_stock_data_ = FunctionTool.from_defaults(fn=load_tea_stock_data)

    agent = ReActAgent.from_tools([call_sales_api_,call_operations_api_,call_dashboard_api_,get_tea_stock_data_], llm=llm, verbose=True)

    agent.update_prompts(prompt_dict)

    response = agent.chat(instructions)
    response = str(response)

    print("====== Executed agent2 ======")

    return(response)




#Agent 3
def call_agent3(instructions):
    """
    Agent 3/ Information Gathering agent  
        This agent specialized and responsible for information gathering from internet, it has capabilities of searching  internet and scraping data. 
        If you want any external information from internet you can simply call this agent and ask to get info
    
    """
    print("====== Executing agent3 ======")


    agent_3 = PromptTemplate(agent_3_prompt)

    prompt_dict = {
        "agent_worker:system_prompt" : agent_3
    }

    llm = OpenAI(model="gpt-4o")

    search_news_ = FunctionTool.from_defaults(fn=search_news)
    google_search_ = FunctionTool.from_defaults(fn=google_search)
    web_scraping_ = FunctionTool.from_defaults(fn=web_scraping)
    realtime_weather_ = FunctionTool.from_defaults(fn=realtime_weather)

    agent = ReActAgent.from_tools([search_news_,google_search_,web_scraping_,realtime_weather_], llm=llm, verbose=True)

    agent.update_prompts(prompt_dict)

    response = agent.chat(instructions)
    response = str(response)

    print("====== Executed agent3 ======")


    return(response)




def call_agent4(instructions):
    """
    Creates charts and graphs based on provided information and instructions
    When you want to show some insights to top management, you can ask this agent to create graphs with information you provide. 
    """
    print("====== Executing agent4 ======")
    print(f"Instructions: {instructions}")

    code_spec = CodeInterpreterToolSpec()
    tools = code_spec.to_tool_list()

    # Create the prompt template
    agent_4_prompt_ = PromptTemplate(agent_4_prompt)

    # Generate tool descriptions and names
    tool_desc = "\n".join([f"{tool.metadata.name}: {tool.metadata.description}" for tool in tools])
    tool_names = ", ".join([tool.metadata.name for tool in tools])

    # Create the OpenAIAgent with the custom prompt
    agent_4 = OpenAIAgent.from_tools(
        tools,
        system_prompt=agent_4_prompt_.format(tool_desc=tool_desc, tool_names=tool_names),
        verbose=True
    )

    # Ensure the graphs folder exists
    os.makedirs("graphs", exist_ok=True)

    response = agent_4.chat(instructions)
    print(f"Agent 4 response: {response}")

    # Check if the graph was actually saved
    if "Graph saved successfully" in str(response):
        graph_path = str(response).split("at ")[-1].strip()
        if os.path.exists(graph_path):
            print(f"Graph file confirmed at: {graph_path}")
        else:
            print(f"Graph file not found at: {graph_path}")

    return response


