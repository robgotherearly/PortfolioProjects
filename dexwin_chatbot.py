import streamlit as st
from anthropic import Anthropic

# Initialize Streamic client
client = Anthropic()

# Page config
st.set_page_config(
    page_title="Dexwin Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 20px;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: right;
    }
    .bot-message {
        background-color: #f5f5f5;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://dexwin.net/dexwin-logo-white.svg", width=80)
with col2:
    st.title("Dexwin AI Assistant")
    st.caption("Ask me anything about Dexwin's services, projects, and capabilities")

# System prompt with Dexwin information
SYSTEM_PROMPT = """You are a helpful customer service chatbot for Dexwin Tech Ltd, a digital product development agency based in Ghana.

COMPANY INFORMATION:
- Dexwin is an end-to-end digital product development agency
- Mission: "Empowering Global Innovation Through African Excellence"
- They provide talent to leading firms looking to expand their product teams
- Based in Ghana and expanding globally

CORE SERVICES:
1. Product Design - Intuitive, user-centered interfaces and user experiences
2. Software Development - Scalable web and mobile app solutions using modern frameworks
3. Data Analytics - Actionable insights from raw data to guide decisions
4. Skills Training - Tailored programs to upskill internal teams
5. Talent Outsourcing - Contract-based or embedded team members across roles and stacks
6. IT Consulting - Wide range of general services to support business operations

DELIVERY MODELS:
- End to End Delivery: Full-cycle project execution from concept to launch
- Supplying Extra Hands: Reinforcing teams with skilled professionals on demand
- Embedded Full Teams: Autonomous teams to lead and deliver client vision

NOTABLE PROJECTS:
1. MyMTN App - Transitioned MTN Ghana's USSD into mobile app (1M+ active users, 127% growth)
2. Saving Grains - Hybrid solution for rural farmers (15K+ farmers reached, 500% growth)
3. MTN Pulse - Digital hub for youth engagement (500K+ engaged, 100K+ daily sessions)
4. MTN Hoods - Top-up experience platform (1K+ transactions/day, 3 taps average)

KEY PARTNERSHIPS:
- MTN Ghana (largest telecom provider)
- GIZ (German development agency)
- The World Bank
- Saving Grains (social enterprise)

Be friendly, professional, and helpful. If asked about something not in this knowledge base, be honest and suggest contacting them directly at https://dexwin.net/gh/contact-us or request a quote."""

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message"><b>You:</b> {message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message"><b>Assistant:</b> {message["content"]}</div>', 
                       unsafe_allow_html=True)

# Input area
st.divider()
user_input = st.chat_input("Type your question here...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response from Claude
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=st.session_state.messages
    )
    
    # Extract assistant response
    assistant_message = response.content[0].text
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
    
    # Rerun to display new messages
    st.rerun()

# Footer with quick actions
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📞 Contact Us", use_container_width=True):
        st.markdown("[Visit Contact Page](https://dexwin.net/gh/contact-us)")
with col2:
    if st.button("🎯 Request a Quote", use_container_width=True):
        st.markdown("[Request Quote](https://dexwin.net/gh/contact-us)")
with col3:
    if st.button("🔍 View Projects", use_container_width=True):
        st.markdown("[View Projects](https://dexwin.net/gh/projects)")

st.markdown("""
---
*Dexwin Chatbot powered by Claude AI | For more info visit [dexwin.net](https://dexwin.net)*
""", unsafe_allow_html=True)