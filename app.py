import streamlit as st
st.set_page_config(page_title="Eat or Fate", page_icon="🎲", layout="wide")
from auth import init_user_db, register_user, verify_user, delete_user
from restaurant import restaurant_app, restaurant_app_test

init_user_db()

st.title("🍽️ Eat or Fate")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

st.sidebar.header("User")

if st.session_state.logged_in:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    if st.sidebar.button("⚠️ Delete My Account"):
        delete_user(st.session_state["username"], st.session_state["username"])

else:
    login_username = st.sidebar.text_input("Username")
    login_password = st.sidebar.text_input("Password", type="password")

    col1, col2 = st.sidebar.columns(2)
    if st.sidebar.button("Login"):
        if verify_user(login_username, login_password):
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")

    if st.sidebar.button("Register"):
        if register_user(login_username, login_password):
            st.sidebar.success("Registration successful. Please log in.")
        else:
            st.sidebar.error("Username already exists.")




if st.session_state.logged_in:
    restaurant_app(st.session_state.username)
else:
    st.info("👤 You are in **Visitor Mode**. Changes won't be saved permanently.")
    restaurant_app_test()
