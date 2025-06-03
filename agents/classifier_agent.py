from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json
import re

def extract_json(text):
    # Try to extract JSON block inside any triple backticks
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        return match.group(1)
    else:
        # If no backticks found, fallback to the entire text (maybe raw JSON)
        return text.strip()
    
class ClassifierAgent:
    def __init__(self, groq_api_key):
        self.llm = ChatGroq(groq_api_key=groq_api_key, model="llama-3.3-70b-versatile", temperature=0.2, model_name="mixtral-8x7b-32768")
        self.prompt = PromptTemplate(
            input_variables=["input_data"],                template="""
    You are an intelligent AI agent that classifies inputs based on format and intent.

    Classify the following input:
    {input_data}

    Return a JSON with two keys: format (pdf, json, email) and intent (RFQ, invoice, complaint, regulation, or any other relevant intent you detect.)
    """
            )
            
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def classify(self, input_data):
        raw_output = self.chain.invoke({"input_data": input_data})
        # print("LLM Raw Output:", raw_output)

        llm_text = raw_output.get("text") if isinstance(raw_output, dict) else str(raw_output)

        json_str = extract_json(llm_text)
        # print("Extracted JSON string:", json_str)

        try:
            parsed = json.loads(json_str)
            if "format" in parsed and "intent" in parsed:
                return parsed
            else:
                print("JSON parsed but missing required keys.")
                return {"format": "unknown", "intent": "unknown"}
        except json.JSONDecodeError as e:
            print("JSON parsing failed:", e)
            return {"format": "unknown", "intent": "unknown"}