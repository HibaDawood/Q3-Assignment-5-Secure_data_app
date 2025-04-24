import streamlit as st
import hashlib
from cryptography.fernet import Fernet
import base64

# Initialize session state variables if they don't exist
if 'stored_data' not in st.session_state:
    st.session_state.stored_data = {}  # {"user1_data": {"encrypted_text": "xyz", "passkey": "hashed"}}

if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0

if 'key' not in st.session_state:
    # Generate a key (this should be stored securely in production)
    st.session_state.key = Fernet.generate_key()
    st.session_state.cipher = Fernet(st.session_state.key)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True  # Start as authenticated

# Function to hash passkey
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Function to encrypt data
def encrypt_data(text, passkey):
    # We don't actually use the passkey for encryption, just for verification
    return st.session_state.cipher.encrypt(text.encode()).decode()

# Function to decrypt data
def decrypt_data(encrypted_text, passkey):
    hashed_passkey = hash_passkey(passkey)
    
    # Check if the encrypted_text exists in our stored data
    if encrypted_text in st.session_state.stored_data:
        # Check if the passkey matches
        if st.session_state.stored_data[encrypted_text]["passkey"] == hashed_passkey:
            st.session_state.failed_attempts = 0
            try:
                return st.session_state.cipher.decrypt(encrypted_text.encode()).decode()
            except Exception:
                return "Error: Invalid encrypted data format"
    
    # Increment failed attempts
    st.session_state.failed_attempts += 1
    return None

# Streamlit UI
st.title("🔒 Secure Data Encryption System")

# Navigation
menu = ["Home", "Store Data", "Retrieve Data", "Login"]
choice = st.sidebar.selectbox("Navigation", menu)

# Display failed attempts if any
if st.session_state.failed_attempts > 0:
    st.sidebar.warning(f"⚠️ Failed attempts: {st.session_state.failed_attempts}/3")

# Check if too many failed attempts
if st.session_state.failed_attempts >= 3:
    st.session_state.authenticated = False
    choice = "Login"  # Force redirect to login

# Home Page
if choice == "Home":
    st.subheader("🏠 Welcome to the Secure Data System")
    st.write("Use this app to **securely store and retrieve data** using unique passkeys.")
    
    st.info("""
    ### How to use this system:
    
    1. **Store Data**: Enter your text and a passkey to encrypt and store your data
    2. **Retrieve Data**: Use your passkey to decrypt and view your stored data
    3. **Security**: After 3 failed attempts, you'll need to reauthorize
    
    All data is stored securely in memory and encrypted using Fernet symmetric encryption.
    """)

# Store Data Page
elif choice == "Store Data":
    if not st.session_state.authenticated:
        st.warning("🔒 Please login first!")
        st.stop()
        
    st.subheader("📂 Store Data Securely")
    
    user_data = st.text_area("Enter Data:", height=150)
    passkey = st.text_input("Enter Passkey:", type="password")
    
    if st.button("Encrypt & Save"):
        if user_data and passkey:
            hashed_passkey = hash_passkey(passkey)
            encrypted_text = encrypt_data(user_data, passkey)
            
            # Store the encrypted data with the hashed passkey
            st.session_state.stored_data[encrypted_text] = {
                "encrypted_text": encrypted_text, 
                "passkey": hashed_passkey
            }
            
            st.success("✅ Data stored securely!")
            
            # Display the encrypted text for the user to copy
            st.code(encrypted_text, language="text")
            st.info("⚠️ Copy this encrypted text - you'll need it to retrieve your data later!")
            
            # Show how many entries are stored
            st.caption(f"Total entries stored: {len(st.session_state.stored_data)}")
        else:
            st.error("⚠️ Both fields are required!")

# Retrieve Data Page
elif choice == "Retrieve Data":
    if not st.session_state.authenticated:
        st.warning("🔒 Please login first!")
        st.stop()
        
    st.subheader("🔍 Retrieve Your Data")
    
    encrypted_text = st.text_area("Enter Encrypted Data:", height=100)
    passkey = st.text_input("Enter Passkey:", type="password")
    
    if st.button("Decrypt"):
        if encrypted_text and passkey:
            decrypted_text = decrypt_data(encrypted_text, passkey)
            
            if decrypted_text:
                st.success("✅ Data decrypted successfully!")
                st.markdown("### Your Decrypted Data:")
                st.markdown(f"""
                <div style="padding: 15px; border-radius: 5px; background-color: #077A7D;">
                {decrypted_text}
                </div>
                """, unsafe_allow_html=True)
            else:
                remaining = 3 - st.session_state.failed_attempts
                st.error(f"❌ Incorrect passkey! Attempts remaining: {remaining}")
                
                if st.session_state.failed_attempts >= 3:
                    st.warning("🔒 Too many failed attempts! Please reauthorize.")
                    st.session_state.authenticated = False
                    st.experimental_rerun()
        else:
            st.error("⚠️ Both fields are required!")

# Login Page
elif choice == "Login":
    st.subheader("🔑 Reauthorization Required")
    
    st.info("You need to reauthorize after too many failed attempts.")
    
    login_pass = st.text_input("Enter Master Password:", type="password")
    
    if st.button("Login"):
        # In a real application, you would use a more secure authentication method
        if login_pass == "admin123":  # Hardcoded for demo, replace with proper auth
            st.session_state.failed_attempts = 0
            st.session_state.authenticated = True
            st.success("✅ Reauthorized successfully!")
            
            # Add a button to navigate back to Retrieve Data
            if st.button("Go to Retrieve Data"):
                choice = "Retrieve Data"
                st.experimental_rerun()
        else:
            st.error("❌ Incorrect password!")

# Display system status in the sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("System Status")
status = "🟢 Authenticated" if st.session_state.authenticated else "🔴 Locked"
st.sidebar.markdown(f"**Status:** {status}")
st.sidebar.markdown(f"**Stored Entries:** {len(st.session_state.stored_data)}")

# Footer
st.markdown("---")


# For demonstration purposes
print("System Status:")
print(f"Authenticated: {st.session_state.authenticated}")
print(f"Failed Attempts: {st.session_state.failed_attempts}")
print(f"Stored Data Entries: {len(st.session_state.stored_data)}")
