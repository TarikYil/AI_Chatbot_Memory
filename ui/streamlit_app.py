import streamlit as st
import requests

# FASTAPI URL (ensure to replace it with your actual API URL)
FASTAPI_URL = "http://api:8014"  # API service in Docker environment

# Set page title and favicon
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",  # You can also provide a file path like "static/favicon.ico" for a custom icon
)

# Clear Short-Term Memory (STM) when the page loads
if "stm_cleared" not in st.session_state:
    try:
        # Request to clear STM at the beginning of the session
        requests.get(f"{FASTAPI_URL}/session/clear")
        st.session_state["stm_cleared"] = True
    except Exception as e:
        # Warning if STM cleanup fails
        st.warning("STM couldn't be cleared: Is the server running?")

def main():
    """
    Main function for running the Jetlink AI Chatbot interface.

    This function initializes the Streamlit app, handles user inputs, displays
    message history, and interacts with the FastAPI backend for both STM and LTM-based chats.
    """
    st.title("AI Chatbot")

    # Initialize the message history if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Sidebar for settings and chat history display
    with st.sidebar:
        st.header("🔧 Settings")

        # Memory type selection (STM or LTM)
        memory_type = st.radio("Select Memory Type", ["LTM (Long-Term Memory)", "STM (Short-Term Memory)"])
        st.divider()

        # Memory management options
        st.subheader("🧠 Memory Management")
        memory_management_option = st.selectbox("Select Operation", ["Delete All Memory", "Clear Session"])

        # Handle 'Delete All Memory' operation
        if memory_management_option == "Delete All Memory":
            if st.button("Delete Memory"):
                try:
                    response = requests.delete(f"{FASTAPI_URL}/memory/delete")
                    response.raise_for_status()
                    st.success(response.json()["message"])
                except requests.exceptions.RequestException as e:
                    st.error(f"Error while deleting memory: {e}")

        # Handle 'Clear Session' operation
        elif memory_management_option == "Clear Session":
            if st.button("Clear Session"):
                try:
                    response = requests.get(f"{FASTAPI_URL}/session/clear")
                    response.raise_for_status()
                    st.session_state["messages"] = []  # Clear chat history in the session state
                    st.success(response.json()["message"])
                except requests.exceptions.RequestException as e:
                    st.error(f"Error while clearing session: {e}")

        # Display chat history in the sidebar
        st.subheader("💬 Chat History")
        for msg in st.session_state["messages"]:
            role = "👤" if msg["role"] == "user" else "🤖"
            st.markdown(f"**{role} {msg['role'].capitalize()}**:\n{msg['content']}", unsafe_allow_html=True)

    # User input and message submission
    prompt = st.chat_input("Type your message here")
    if prompt:
        # Add user message to the session
        st.session_state["messages"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        try:
            # Decide which endpoint to call based on memory type (STM or LTM)
            endpoint = "stm" if memory_type == "STM (Short-Term Memory)" else "ltm"
            response = requests.post(f"{FASTAPI_URL}/chat/{endpoint}", json={"role": "user", "content": prompt})
            response.raise_for_status()

            # Get the assistant's response
            assistant_response = response.json()["response"]
            st.session_state["messages"].append({"role": "assistant", "content": assistant_response})
            st.chat_message("assistant").write(assistant_response)
        except requests.exceptions.RequestException as e:
            st.error(f"Error during API request: {e}")

if __name__ == "__main__":
    main()
