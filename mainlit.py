import streamlit as st
from ascii import ascii_app
from csteg import steg
from anj import gif

# Function to load custom CSS from a file
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    # Load external CSS
    load_css("style.css")

    # Default active app
    if "active_app" not in st.session_state:
        st.session_state.active_app = "App 1"

    # Sidebar navigation
    st.sidebar.title("Application Navigator")
    if st.sidebar.button("ASCII Characters"):
        st.session_state.active_app = "App 1"
    if st.sidebar.button("Stegnography"):
        st.session_state.active_app = "App 2"
    if st.sidebar.button("Encode into gif"):
        st.session_state.active_app = "App 3"

    # Main content
    if st.session_state.active_app == "App 1":
        ascii_app()
    elif st.session_state.active_app == "App 2":
        steg()
    elif st.session_state.active_app == "App 3":
        gif()

if __name__ == "__main__":
    main()
