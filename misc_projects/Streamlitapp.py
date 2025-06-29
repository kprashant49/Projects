import streamlit as st

st.title("Simple Streamlit App")

name = st.text_input("Enter your name:")
st.write("Hello", name)
