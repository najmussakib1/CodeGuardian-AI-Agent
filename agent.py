import os
import difflib
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import utils

load_dotenv()

# Define State
class AgentState(TypedDict):
    filepath: str
    code: str
    errors: Optional[str]
    fixed_code: Optional[str]
    patch: Optional[str]
    status: str
    dry_run: bool

# Initialize LLM
llm = ChatGroq(
    temperature=0,
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Nodes
def check_code(state: AgentState):
    filepath = state["filepath"]
    print(f"Checking {filepath}...")
    lint_result = utils.lint_file(filepath)
    
    # If return code is 0, mostly no errors, but let's check stdout/stderr
    # Pylint exit codes: 0=no error, >0 error.
    # However, we might want to catch non-zero exit codes.
    
    if lint_result["returncode"] == 0:
        return {"errors": None, "status": "clean"}
    
    errors = f"STDOUT:\n{lint_result['stdout']}\nSTDERR:\n{lint_result['stderr']}"
    # Read file content to pass to fixer
    code = utils.read_file(filepath)
    return {"errors": errors, "code": code, "status": "needs_fix"}

def analyze_and_fix(state: AgentState):
    code = state["code"]
    errors = state["errors"]
    
    print("Analyzing and fixing...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Python developer. You are given a python file content and a list of linting/execution errors. Fix the code to resolve the errors. Return ONLY the fixed code. Do not include markdown backticks or explanations."),
        ("user", "Code:\n{code}\n\nErrors:\n{errors}")
    ])
    
    chain = prompt | llm
    result = chain.invoke({"code": code, "errors": errors})
    fixed_code = result.content.strip()
    
    # Clean up if model outputs backticks
    if fixed_code.startswith("```"):
        fixed_code = fixed_code.split("\n", 1)[1]
    if fixed_code.endswith("```"):
        fixed_code = fixed_code.rsplit("\n", 1)[0]
        
    patch = utils.generate_patch(code, fixed_code, state["filepath"])
    
    return {"fixed_code": fixed_code, "patch": patch}

def save_results(state: AgentState):
    print("Saving results...")
    filepath = state["filepath"]
    fixed_code = state["fixed_code"]
    patch = state["patch"]
    errors = state["errors"]
    
    # Apply fix
    utils.apply_fix(filepath, fixed_code)
    
    # Log result
    utils.log_result(filepath, errors, fixed_code, patch)
    
    return {"status": "fixed"}

# Edges
def route_check(state: AgentState):
    if state["status"] == "clean":
        return END
    return "analyze_and_fix"

def route_analyze(state: AgentState):
    if state.get("dry_run", False):
        return END
    return "save_results"

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("check_code", check_code)
workflow.add_node("analyze_and_fix", analyze_and_fix)
workflow.add_node("save_results", save_results)

workflow.set_entry_point("check_code")

workflow.add_conditional_edges(
    "check_code",
    route_check,
    {
        END: END,
        "analyze_and_fix": "analyze_and_fix"
    }
)

workflow.add_conditional_edges(
    "analyze_and_fix",
    route_analyze,
    {
        END: END,
        "save_results": "save_results"
    }
)

workflow.add_edge("save_results", END)

app = workflow.compile()

def run_agent(filepath, dry_run=False):
    initial_state = {
        "filepath": filepath,
        "code": "",
        "errors": None,
        "fixed_code": None,
        "patch": None,
        "status": "start",
        "dry_run": dry_run
    }
    result = app.invoke(initial_state)
    return result
