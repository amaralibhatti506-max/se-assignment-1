import pandas as pd
import requests
import streamlit as st

API = "http://127.0.0.1:5000/students"

st.set_page_config(page_title="Student Management", layout="centered")
st.title("🎓 Student Management")


def fetch_students():
    try:
        r = requests.get(API, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        st.error(f"Cannot reach Flask API: {e}")
        return []


def show_result(resp, ok_msg):
    if resp.ok:
        st.success(ok_msg)
        st.rerun()  # refresh displayed records
    else:
        st.error(resp.json().get("error", "Request failed"))


students = fetch_students()

st.subheader("All students")
if students:
    st.dataframe(pd.DataFrame(students), use_container_width=True, hide_index=True)
else:
    st.info("No students yet.")

st.divider()
st.subheader("Add student")
with st.form("add_form", clear_on_submit=True):
    name = st.text_input("Name")
    dept = st.text_input("Department")
    email = st.text_input("Email")
    if st.form_submit_button("Add"):
        if not (name.strip() and dept.strip() and email.strip()):
            st.warning("Fill in all fields.")
        else:
            show_result(
                requests.post(API, json={"name": name, "department": dept, "email": email}),
                "Student added.",
            )

if students:
    st.divider()
    st.subheader("Update student")
    labels = {f"{s['id']} - {s['name']}": s for s in students}
    choice = labels[st.selectbox("Select student", list(labels), key="upd_sel")]
    with st.form("update_form"):
        n = st.text_input("Name", choice["name"], key=f"n{choice['id']}")
        d = st.text_input("Department", choice["department"], key=f"d{choice['id']}")
        e = st.text_input("Email", choice["email"], key=f"e{choice['id']}")
        if st.form_submit_button("Update"):
            show_result(
                requests.put(f"{API}/{choice['id']}", json={"name": n, "department": d, "email": e}),
                "Student updated.",
            )

    st.divider()
    st.subheader("Delete student")
    del_choice = labels[st.selectbox("Select student to delete", list(labels), key="del_sel")]
    if st.button("Delete", type="primary"):
        show_result(requests.delete(f"{API}/{del_choice['id']}"), "Student deleted.")
