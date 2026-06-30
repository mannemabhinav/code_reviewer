import streamlit as st
import tempfile
import subprocess
import os
import sys
import pandas as pd
import black
from radon.complexity import cc_visit, cc_rank

# ==================================
# PAGE CONFIG
# ==================================
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Code Reviewer")
st.write("Analyze Python code quality using Flake8, Black and Radon.")

# ==================================
# FILE UPLOAD
# ==================================
uploaded_file = st.file_uploader(
    "Upload Python File",
    type=["py"]
)

if uploaded_file:

    code = uploaded_file.read().decode("utf-8")

    st.subheader("📄 Uploaded Code")
    st.code(code, language="python")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".py",
        mode="w",
        encoding="utf-8"
    ) as temp_file:

        temp_file.write(code)
        temp_path = temp_file.name

    # ==================================
    # FLAKE8 ANALYSIS
    # ==================================
    st.subheader("🔍 Style Analysis (Flake8)")

    issue_count = 0
    flake_output = ""

    try:

        flake_result = subprocess.run(
            [sys.executable, "-m", "flake8", temp_path],
            capture_output=True,
            text=True
        )

        flake_output = flake_result.stdout

        # Replace temp path with uploaded file name
        flake_output = flake_output.replace(
            temp_path,
            uploaded_file.name
        )

        if flake_output.strip():

            st.error("❌ Style Issues Found")

            st.code(
                flake_output,
                language="text"
            )

            issue_count = len(
                flake_output.strip().split("\n")
            )

        else:

            st.success(
                "✅ No Style Issues Found"
            )

    except Exception as e:

        st.error(
            f"Flake8 Error: {e}"
        )

    # ==================================
    # CODE QUALITY SCORE
    # ==================================
    score = max(0, 100 - issue_count)

    st.subheader("📈 Code Quality Score")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Quality Score",
            f"{score}/100"
        )

    with col2:
        st.metric(
            "Issues Found",
            issue_count
        )

    # ==================================
    # BLACK FORMATTER
    # ==================================
    st.subheader("✨ Auto Formatting (Black)")

    try:

        formatted_code = black.format_str(
            code,
            mode=black.FileMode()
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Original Code")
            st.code(
                code,
                language="python"
            )

        with col2:
            st.markdown("### Formatted Code")
            st.code(
                formatted_code,
                language="python"
            )

    except Exception as e:

        st.error(
            f"Formatting Error: {e}"
        )

        formatted_code = code

    # ==================================
    # RADON ANALYSIS
    # ==================================
    st.subheader("📊 Complexity Analysis")

    try:

        results = cc_visit(code)

        if results:

            complexity_data = []

            for item in results:

                complexity_data.append({
                    "Function": item.name,
                    "Line Number": item.lineno,
                    "Complexity": item.complexity,
                    "Rank": cc_rank(item.complexity)
                })

            df = pd.DataFrame(
                complexity_data
            )

            st.dataframe(
                df,
                use_container_width=True
            )

        else:

            st.info(
                "No functions found in code."
            )

    except Exception as e:

        st.error(
            f"Radon Error: {e}"
        )

    # ==================================
    # AI SUGGESTIONS
    # ==================================
    st.subheader("💡 AI Suggestions")

    suggestions = []

    if len(code.splitlines()) > 100:
        suggestions.append(
            "Large file detected. Consider splitting into modules."
        )

    if "global " in code:
        suggestions.append(
            "Avoid using global variables."
        )

    if "print(" in code:
        suggestions.append(
            "Use logging instead of print statements."
        )

    if "except:" in code:
        suggestions.append(
            "Avoid bare except statements."
        )

    if "== None" in code:
        suggestions.append(
            "Use 'is None' instead of '== None'."
        )

    if issue_count > 10:
        suggestions.append(
            "Too many style issues detected. Refactor the code."
        )

    if score < 70:
        suggestions.append(
            "Code quality score is low. Improve readability and maintainability."
        )

    if suggestions:

        for suggestion in suggestions:
            st.warning(
                suggestion
            )

    else:

        st.success(
            "🎉 Excellent code quality!"
        )

    # ==================================
    # REPORT GENERATION
    # ==================================
    st.subheader("📥 Download Report")

    report = f"""
AI CODE REVIEW REPORT

====================================

File Name:
{uploaded_file.name}

====================================

Total Lines:
{len(code.splitlines())}

====================================

Quality Score:
{score}/100

====================================

Issues Found:
{issue_count}

====================================

Flake8 Output:

{flake_output}

====================================

Suggestions:

"""

    if suggestions:

        for suggestion in suggestions:
            report += f"- {suggestion}\n"

    else:
        report += "- No major issues found.\n"

    st.download_button(
        label="📄 Download Report",
        data=report,
        file_name="AI_Code_Review_Report.txt",
        mime="text/plain"
    )

    # ==================================
    # CLEANUP
    # ==================================
    try:
        os.remove(temp_path)
    except:
        pass