import streamlit as st
import requests

# Streamlit UI
st.title("Recommendation System")
st.write("Enter your user hash to get personalized recommendations.")

# User input for hash
user_hash = st.text_input("User Hash", placeholder="Enter your hash...")

# Button to send request
if st.button("Get Recommendation"):
    if user_hash:
        # Define API endpoint
        api_url = "http://fastapi:8000/recommendation"  # Change this URL if needed

        # Prepare payload
        payload = {"hash": user_hash}

        try:
            # Make the POST request
            response = requests.post(api_url, json=payload)
            
            if response.status_code == 200:
                # Display response
                st.success("Recommendations received!")
                st.json(response.json())  # Show JSON response
            else:
                st.error(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
    else:
        st.warning("Please enter a valid user hash.")

