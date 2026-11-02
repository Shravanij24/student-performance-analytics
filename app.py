
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Page configuration
st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="📊",
    layout="wide"
)

# 2. Custom dashboard styling
# 2. Custom dashboard styling
st.markdown("""
<style>
    .stApp {
        background-color: #F7F8FC;
        color: #28345C;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #F7F8FC;
    }

    [data-testid="stSidebar"] {
        background-color: #EEF0FA;
    }

    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li,
    label,
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: #28345C !important;
    }

    h1, h2, h3, h4 {
        color: #28345C !important;
    }

    h1 {
        font-weight: 800;
    }

    h2, h3 {
        font-weight: 700;
    }

    [data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #DDE1F0;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(40,52,92,0.08);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E2E5F0;
        border-radius: 10px;
    }

    .stButton button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Dashboard heading
st.title("📊 Student Performance Analytics")
st.write("Analyze student marks and understand academic performance.")

# 3. Define required columns
subjects = ["Math", "Science", "English", "Computer"]

required_columns = [
    "Student_ID", "Name", "Gender",
    "Math", "Science", "English", "Computer"
]

# 4. CSV upload option
st.sidebar.header("Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload student CSV file",
    type=["csv"]
)

# 5. Read uploaded or sample dataset
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Your CSV file was uploaded successfully!")
    except Exception:
        st.error("Unable to read this CSV file. Please check the file.")
        st.stop()
else:
    df = pd.read_csv("students.csv")
    st.sidebar.info("Currently using sample student data.")

# 6. Validate dataset
missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

if df.empty:
    st.error("The uploaded dataset is empty.")
    st.stop()

if df[["Name", "Gender"]].isnull().any().any():
    st.error("Name and Gender cannot contain empty values.")
    st.stop()

# Convert subject marks into numeric values
df[subjects] = df[subjects].apply(
    pd.to_numeric, errors="coerce"
)

if df[subjects].isnull().any().any():
    st.error("Subject marks must contain valid numbers.")
    st.stop()

if ((df[subjects] < 0) | (df[subjects] > 100)).any().any():
    st.error("Marks must be between 0 and 100.")
    st.stop()

# Passing marks setting 
st.sidebar.header("Pass/Fail Settings")

passing_marks = st.sidebar.slider(
    "Minimum passing marks",
    min_value=0,
    max_value=100,
    value=40
)

# 7. Calculate average marks
df["Average"] = df[subjects].mean(axis=1)
# Identify subjects where students failed
df["Failed Subjects"] = df[subjects].apply(
    lambda row: ", ".join(
        row.index[row < passing_marks].tolist()
    ),
    axis=1
)

# Assign Pass or Fail
df["Result"] = df["Failed Subjects"].apply(
    lambda x: "Fail" if x else "Pass"
)

# 8. Sidebar gender filter
st.sidebar.header("Filter Students")

gender_options = ["All"] + sorted(
    df["Gender"].unique().tolist()
)

selected_gender = st.sidebar.selectbox(
    "Select Gender",
    gender_options
)

if selected_gender != "All":
    filtered_df = df[
        df["Gender"] == selected_gender
    ]
else:
    filtered_df = df.copy()

# Grade Distribution
filtered_df = filtered_df.copy()

filtered_df["Grade"] = pd.cut(
    filtered_df["Average"],
    bins=[0, 60, 70, 80, 90, 101],
    labels=[
        "Needs Improvement",
        "D",
        "C",
        "B",
        "A"
    ],
    right=False
)

# 9. Overall performance
st.subheader("📌 Overall Performance")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Students", len(filtered_df))

col2.metric(
    "Average Marks",
    round(filtered_df["Average"].mean(), 2)
)

col3.metric(
    "Highest Average",
    round(filtered_df["Average"].max(), 2)
)

col4.metric(
    "Lowest Average",
    round(filtered_df["Average"].min(), 2)
)

st.divider()

# 10. Student records
# Grade Distribution Chart
st.subheader("🏆 Grade Distribution")

grade_order = [
    "A",
    "B",
    "C",
    "D",
    "Needs Improvement"
]

grade_counts = (
    filtered_df["Grade"]
    .value_counts()
    .reindex(grade_order, fill_value=0)
)

fig, ax = plt.subplots(figsize=(8, 4))

ax.barh(grade_counts.index, grade_counts.values)

ax.set_title("Number of Students in Each Grade")
ax.set_xlabel("Number of Students")
ax.set_ylabel("Grade")

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
# Pass/Fail Analysis
st.subheader("📋 Pass/Fail Analysis")

pass_count = len(
    filtered_df[filtered_df["Result"] == "Pass"]
)

fail_count = len(
    filtered_df[filtered_df["Result"] == "Fail"]
)

total = len(filtered_df)

pass_percentage = (
    (pass_count / total) * 100 if total > 0 else 0
)

col1, col2, col3 = st.columns(3)

col1.metric("Passed Students", pass_count)
col2.metric("Failed Students", fail_count)
col3.metric("Pass Percentage", f"{pass_percentage:.2f}%")

st.write("Detailed student results:")

st.dataframe(
    filtered_df[
        ["Student_ID", "Name", "Average",
         "Failed Subjects", "Result"]
    ],
    use_container_width=True,
    hide_index=True
)
st.subheader("👩‍🎓 Student Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# 11. Subject-wise performance chart
st.subheader("📈 Subject-wise Average Marks")

subject_averages = filtered_df[subjects].mean()

fig, ax = plt.subplots(figsize=(9, 4))

subject_averages.plot(kind="bar", ax=ax)

ax.set_ylabel("Average Marks")
ax.set_xlabel("Subjects")
ax.set_ylim(0, 100)
ax.set_title("Average Performance in Each Subject")

plt.xticks(rotation=0)
plt.tight_layout()

st.pyplot(fig)
plt.close(fig)

# 12. Students needing improvement
st.subheader("⚠️ Students Needing Improvement")

needs_improvement = filtered_df[
    filtered_df["Average"] < 60
]

if len(needs_improvement) > 0:
    st.write("Students with an average below 60 marks:")

    st.dataframe(
        needs_improvement[
            ["Student_ID", "Name", "Average"]
        ],
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("No students are below the 60-mark average.")

st.caption(
    "This dashboard uses student data for academic analysis."
)

