import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database setup
DATABASE_URL = "sqlite:///spending.db"
Base = declarative_base()


class Spending(Base):
    __tablename__ = 'spending'
    id = Column(Integer, primary_key=True, autoincrement=True)
    member = Column(String, nullable=False)
    item = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    date = Column(Date, nullable=False, default=datetime.now().date)


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


# Function to add spending to the database
def add_spending(member, item, cost, date):
    new_spending = Spending(member=member, item=item, cost=cost, date=date)
    session.add(new_spending)
    session.commit()


# Function to update spending in the database
def update_spending(id, member, item, cost, date):
    spending = session.query(Spending).filter(Spending.id == id).first()
    if spending:
        spending.member = member
        spending.item = item
        spending.cost = cost
        spending.date = date
        session.commit()
        return True
    return False


# Function to get all spending data from the database
def get_spending_data():
    return pd.read_sql(session.query(Spending).statement, session.bind)


# Function to get a single spending entry by ID
def get_spending_by_id(id):
    return session.query(Spending).filter(Spending.id == id).first()


st.set_page_config(page_title="Poultry Spending Tracker", layout="wide")

st.title("🐔 Poultry Spending Tracker 🐔")

# Set the background color and other styles
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f8ff;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        margin: 5px;
        transition: transform 0.3s, background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .add-button {
        background-color: #4CAF50;
    }
    .add-button:hover {
        background-color: #45a049;
    }
    .edit-button {
        background-color: #2196F3;
    }
    .edit-button:hover {
        background-color: #0b7dda;
    }
    .update-button {
        background-color: #f39c12;
    }
    .update-button:hover {
        background-color: #e67e22;
    }
    .css-1aumxhk.e1fqkh3o3 {
        border: 2px solid #4CAF50 !important;
        border-radius: 8px;
    }
    .css-1aumxhk.e1fqkh3o3:hover {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    .stTabs .css-18ni7ap.e13qjvis2 {
        font-weight: bold;
    }
    .stTabs .stTabs-label {
        font-weight: bold;
        color: #FF6347;
    }
    .stTabs .stTabs-label:hover {
        color: #FF4500;
    }
    /* Responsive design for mobile */
    @media (max-width: 768px) {
        .stApp {
            padding: 10px;
        }
        .stButton>button {
            width: 100%;
            margin: 10px 0;
            padding: 12px 20px;
        }
        .stTabs .stTabs-label {
            font-size: 14px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Add Spending", "View/Edit Spending", "Summary & Filter"])

# Global state for confirmation
if "show_confirm" not in st.session_state:
    st.session_state.show_confirm = False
if "edit_confirm" not in st.session_state:
    st.session_state.edit_confirm = False

with tab1:
    st.markdown("### Add a new spending entry")
    with st.form(key='spending_form'):
        member = st.selectbox('Select Member', ['George', 'Lourdumary', 'Poondi'])
        item = st.text_input('Item')
        cost = st.number_input('Cost (₹)', min_value=0.0, step=0.1)
        date = st.date_input('Date', value=datetime.now().date())
        confirm_button = st.form_submit_button(label='Confirm')

    # Show confirmation popup
    if confirm_button:
        st.session_state.show_confirm = True

    if st.session_state.show_confirm:
        st.write(f"Are you sure you want to add this entry: {member} spent ₹{cost:.0f} on {item} on {date}?")
        if st.button('Yes, add this entry'):
            add_spending(member, item, cost, date)
            st.success(f"Added spending: {member} spent ₹{cost:.0f} on {item} on {date}")
            st.session_state.show_confirm = False
        elif st.button('No, go back'):
            st.warning("Entry not added.")
            st.session_state.show_confirm = False

with tab2:
    st.markdown("### Search and Edit Spending Data")
    search_member = st.selectbox('Filter by Member', ['All', 'George', 'Lourdumary', 'Poondi'])
    spending_data = get_spending_data()
    if search_member != 'All':
        spending_data = spending_data[spending_data['member'] == search_member]

    # Display the spending data
    spending_data_df = spending_data.copy()
    spending_data_df['ID'] = spending_data_df.index + 1
    spending_data_df['cost'] = spending_data_df['cost'].apply(lambda x: f"₹{x:.0f}")
    st.dataframe(spending_data_df[['ID', 'member', 'item', 'cost', 'date']].style.set_properties(
        **{'background-color': '#ffebcd', 'color': 'black'}))

    # Edit functionality
    st.markdown("### Edit Spending Entry")
    edit_id = st.number_input('Enter ID to Edit', min_value=1, step=1)
    spending_entry = None

    if st.button('Load Entry', key='load_button'):
        spending_entry = get_spending_by_id(edit_id)
        if spending_entry:
            st.session_state.edit_member = spending_entry.member
            st.session_state.edit_item = spending_entry.item
            st.session_state.edit_cost = spending_entry.cost
            st.session_state.edit_date = spending_entry.date

    if spending_entry:
        with st.form(key='edit_form'):
            member = st.selectbox('Edit Member', ['George', 'Lourdumary', 'Poondi'],
                                  index=['George', 'Lourdumary', 'Poondi'].index(st.session_state.edit_member))
            item = st.text_input('Edit Item', value=st.session_state.edit_item)
            cost = st.number_input('Edit Cost (₹)', value=st.session_state.edit_cost, min_value=0.0, step=0.1)
            date = st.date_input('Edit Date', value=st.session_state.edit_date)
            update_button = st.form_submit_button(label='Update Spending')

            if update_button:
                if update_spending(edit_id, member, item, cost, date):
                    st.success(f"Updated spending ID {edit_id}: {member} spent ₹{cost:.0f} on {item} on {date}")
                    # Refresh the data after update
                    spending_data = get_spending_data()
                    if search_member != 'All':
                        spending_data = spending_data[spending_data['member'] == search_member]
                    spending_data_df = spending_data.copy()
                    spending_data_df['ID'] = spending_data_df.index + 1
                    spending_data_df['cost'] = spending_data_df['cost'].apply(lambda x: f"₹{x:.0f}")
                    st.dataframe(spending_data_df[['ID', 'member', 'item', 'cost', 'date']].style.set_properties(
                        **{'background-color': '#ffebcd', 'color': 'black'}))
                else:
                    st.error(f"No entry found with ID {edit_id}")

with tab3:
    st.markdown("### Summary by Member")
    summary_member = st.selectbox('Select Member for Summary', ['All', 'George', 'Lourdumary', 'Poondi'])

    summary_data = get_spending_data()
    if summary_member != 'All':
        summary_data = summary_data[summary_data['member'] == summary_member]

    summary = summary_data.groupby('member')['cost'].sum().reset_index()
    summary['cost'] = summary['cost'].apply(lambda x: f"₹{x:.0f}")
    summary.index = summary.index + 1
    summary.index.name = 'ID'
    st.dataframe(summary.style.set_properties(**{'background-color': '#98fb98', 'color': 'black'}))

    # Display the total cost spent
    total_cost = summary_data['cost'].sum()
    st.markdown(f"### Total Cost Spent: ₹{total_cost:.0f}")

    # Add some styling to the total cost display
    st.markdown(
        f"""
        <div style="color: #2e8b57; font-size: 24px; font-weight: bold;">
            Total Cost Spent: ₹{total_cost:.0f}
        </div>
        """,
        unsafe_allow_html=True
    )
