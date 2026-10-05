import os
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()
api_key = os.getenv("NEBIUS_API_KEY")

# 2. Configure Streamlit Page
st.set_page_config(page_title="Contract Guardian AI", page_icon="🛡️", layout="wide")

st.title("🛡️ Contract Guardian AI")
st.caption("Powered by Nebius Token Factory & NVIDIA Nemotron")

# 3. Setup Nebius Client
# Nebius Token Factory is 100% compatible with the standard OpenAI SDK
client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1",
    api_key=api_key
)

# 4. Helper function to read PDF text
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

# 5. UI Layout: Input Section
st.subheader("1. Provide Your Agreement or Document")
upload_option = st.radio("Choose input method:", ("Upload PDF", "Paste Raw Text"), horizontal=True)

contract_text = ""

if upload_option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a contract (PDF)", type=["pdf"])
    if uploaded_file:
        contract_text = extract_text_from_pdf(uploaded_file)
        st.success(f"Loaded {len(contract_text)} characters from document.")
else:
    contract_text = st.text_area("Paste contract clauses here:", height=200)

# 6. Analyze Button & Nemotron Inference
if st.button("🔍 Audit Contract for Risks", type="primary"):
    if not contract_text.strip():
        st.error("Please provide contract text or upload a PDF first.")
    else:
        with st.spinner("NVIDIA Nemotron is auditing the contract for hidden liabilities..."):
            
            system_prompt = """
            You are an expert contract reviewer and consumer rights advocate.
            Analyze the provided contract text and output your audit in the following markdown structure:
            
            ### 🚦 Executive Risk Score
            Give an overall rating: LOW, MEDIUM, or HIGH RISK with a one-sentence summary.
            
            ### 🚩 Flagged Unfair or Dangerous Clauses
            List every clause that is one-sided, creates unreasonable liability, or imposes hidden penalties.
            For each clause:
            - **Clause Summary**: What it says.
            - **The Hidden Trap**: Why it harms the user or freelancer.
            - **Safer Counter-Proposal**: How to rewrite it fairly.
            
            ### 💡 Next Steps for Negotiation
            Give 2-3 bullet points on how to respond to the other party professionally.
            """

            try:
                response = client.chat.completions.create(
                    model="nvidia/Nemotron-3_5-Lightning",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Review this document:\n\n{contract_text[:12000]}"}
                    ],
                    temperature=0.2,
                )
                
                audit_result = response.choices[0].message.content
                
                st.divider()
                st.subheader("2. Audit Report")
                st.markdown(audit_result)
                
            except Exception as e:
                st.error(f"Error calling Nebius API: {e}")