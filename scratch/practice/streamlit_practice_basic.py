# Streamlit 基礎
import streamlit as st

st.title("My App")
st.write("Hello Streamlit")

st.title("タイトル")
st.header("見出し")
st.write("普通のテキスト")
st.text("シンプルテキスト")

value = 25
st.write("温度：", value)

if st.button("押して"):
    st.write("ボタン押された")