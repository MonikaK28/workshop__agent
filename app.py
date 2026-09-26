import ast
import operator

import streamlit as st


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _evaluate(node):
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        return _BINARY_OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Use numbers, parentheses, and basic arithmetic operators only.")


def calc(expression):
    """Evaluate basic arithmetic without executing arbitrary Python code."""
    return _evaluate(ast.parse(expression, mode="eval"))


def agent(goal):
    """Handle calculator goals in the form 'calculate <expression>'."""
    prefix = "calculate"
    if not goal.lower().startswith(prefix):
        raise ValueError("I can only handle goals that start with 'calculate'.")
    expression = goal[len(prefix):].strip()
    if not expression:
        raise ValueError("Enter an arithmetic expression to calculate.")
    return calc(expression)


st.set_page_config(page_title="Calc Agent", page_icon="🧮", layout="centered")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(145deg, #f5f7ff 0%, #eef6ff 100%); }
    .block-container { max-width: 760px; padding-top: 3rem; }
    .hero { padding: 1.8rem 2rem; border-radius: 24px; color: white;
        background: linear-gradient(120deg, #4338ca, #2563eb 65%, #0891b2);
        box-shadow: 0 18px 45px rgba(37, 99, 235, .20); margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; font-size: 2.2rem; }
    .hero p { color: #e0e7ff; margin: .55rem 0 0; }
    [data-testid="stForm"] { background: white; padding: 1.5rem;
        border: 1px solid #e2e8f0; border-radius: 20px;
        box-shadow: 0 12px 32px rgba(15, 23, 42, .07); }
    @media (max-width: 600px) {
        .block-container { padding-top: 1rem; }
        .hero { padding: 1.2rem; border-radius: 18px; }
        .hero h1 { font-size: 1.7rem; white-space: nowrap; }
        .hero p { font-size: .95rem; }
        [data-testid="stForm"] { padding: 1rem; }
    }
    </style>
    <div class="hero">
      <h1>🧮 Calc Agent</h1>
      <p>Enter an expression and let your simple calculator agent solve it.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

result_area = st.container()

with st.form("calculator_form"):
    expression = st.text_input(
        "Expression",
        placeholder="Try: (25 * 4) + 19",
        help="Supports +, -, *, /, //, %, **, parentheses, and decimal numbers.",
    )
    submitted = st.form_submit_button("✨ Calculate", use_container_width=True)

if submitted:
    if not expression.strip():
        st.session_state.last_error = "Enter an expression first."
        st.session_state.pop("last_result", None)
    else:
        try:
            result = agent(f"calculate {expression}")
            st.session_state.last_result = (expression, result)
            st.session_state.pop("last_error", None)
            history = st.session_state.setdefault("history", [])
            history.insert(0, {"expression": expression, "result": result})
            del history[10:]
        except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError) as error:
            st.session_state.last_error = f"Could not calculate that expression: {error}"
            st.session_state.pop("last_result", None)

with result_area:
    if st.session_state.get("last_error"):
        st.error(st.session_state.last_error)
    elif st.session_state.get("last_result"):
        last_expression, last_result = st.session_state.last_result
        st.success(f"{last_expression} = {last_result}")
        st.metric("Answer", last_result)

if st.session_state.get("history"):
    st.subheader("Recent calculations")
    for item in st.session_state.history:
        st.markdown(f"**`{item['expression']}`**  =  **{item['result']}**")

st.caption("For safety, only arithmetic expressions are evaluated; Python code is not executed.")
