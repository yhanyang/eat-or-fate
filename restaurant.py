import streamlit as st
import pandas as pd
import sqlite3
import os
import time


DATA_FOLDER = "restaurants"
os.makedirs(DATA_FOLDER, exist_ok=True)
TEST_DATA_FILE = os.path.join(DATA_FOLDER, "test_restaurants.csv")


def restaurant_app(username):
    st.header(f"🍴 Welcome, {username}!")

    db_file = os.path.join(DATA_FOLDER, f"{username}.db")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT
        )
    """)
    conn.commit()

    if "user_data" not in st.session_state:
        st.session_state.user_data = pd.read_sql_query("SELECT * FROM restaurants", conn)

    _restaurant_ui(db_mode=True, conn=conn)

    conn.close()


def restaurant_app_test():
    if "test_data" not in st.session_state:
        if os.path.exists(TEST_DATA_FILE):
            st.session_state.test_data = pd.read_csv(TEST_DATA_FILE)
        else:
            st.session_state.test_data = pd.DataFrame(columns=["name", "type"])

    _restaurant_ui(db_mode=False, conn=None)


def _restaurant_ui(db_mode, conn):
    st.subheader("🎲 Random Restaurant Picker")

    df = st.session_state.user_data if db_mode else st.session_state.test_data

    types = df["type"].unique().tolist() if not df.empty else []
    selected_type = st.selectbox("Preferred type:", ["Any"] + types)
    exclude_list = st.multiselect("Exclude these restaurants:", df["name"].tolist() if not df.empty else [])

    if st.button("🎯 Pick Randomly"):
        msg = st.toast('Fate is deciding...')
        time.sleep(1)

        filtered = df[~df["name"].isin(exclude_list)].copy()
        if selected_type != "Any":
            filtered = filtered[filtered["type"] == selected_type]

        if filtered.empty:
            st.warning("No matching restaurant found.")
        else:
            choice = filtered.sample(1).iloc[0]
            msg.toast("Ready!")
            st.success(f"🍴 How about **{choice['name']}** ({choice['type']})?")

    expander = st.expander("➕ Add New Restaurant")
    name = expander.text_input("Restaurant name")
    type_ = expander.text_input("Type (e.g., Japanese, Italian, Fast Food)")

    if expander.button("Add"):
        if name and type_:
            if db_mode:
                conn.execute("INSERT INTO restaurants (name, type) VALUES (?, ?)", (name, type_))
                conn.commit()
                st.session_state.user_data = pd.read_sql_query("SELECT * FROM restaurants", conn)
            else:
                st.session_state.test_data = pd.concat(
                    [st.session_state.test_data, pd.DataFrame([[name, type_]], columns=["name", "type"])],
                    ignore_index=True
                )
            st.toast(f"✅ **{name}** added successfully.")
        else:
            expander.warning("Please fill in all fields.")


    df = st.session_state.user_data if db_mode else st.session_state.test_data

    expander = st.expander("🗑️ Remove Restaurant")
    expander.warning("⚠️ Warning: It will directly modify your SQLite database if you are not in Visitor mode!")

    for idx, row in df.iterrows():
        col1, col2 = expander.columns([3, 7])
        with col2:
            st.write(f"**{row['name']}** ({row['type']})")
        with col1:
            if st.button("Delete", key=f"del_{idx}"):
                if db_mode:
                    conn.execute("DELETE FROM restaurants WHERE id=?", (row['id'],))
                    conn.commit()
                    st.session_state.user_data = pd.read_sql_query("SELECT * FROM restaurants", conn)
                else:
                    st.session_state.test_data = st.session_state.test_data.drop(idx).reset_index(drop=True)
                st.toast(f"🗑️ **{row['name']}** deleted.")

