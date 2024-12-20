import streamlit as st
import streamlit.components.v1 as components
import hashlib
# CSS for Background Image and Styling
background_css = """
<style>
    body {
        background-image: url('https://source.unsplash.com/1600x900/?technology,security');
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Roboto', sans-serif;
        color: #ffffff;
    }
    .container {
        max-width: 800px;
        margin: 40px auto;
        padding: 30px;
        background-color: rgba(0, 0, 0, 0.75);
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
    }
    .header {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 600;
        color: #00b4d8;
        margin-bottom: 20px;
    }
    .subtext {
        text-align: center;
        font-size: 1rem;
        color: #b3d9ff;
        margin-bottom: 30px;
    }
    .btn-primary {
        background-color: #00b4d8;
        border: none;
        padding: 10px 20px;
        font-size: 1rem;
        border-radius: 5px;
        transition: 0.3s ease;
    }
    .btn-primary:hover {
        background-color: #0077b6;
        transform: scale(1.05);
    }
    textarea, input {
        background-color: #222;
        border: 1px solid #555;
        color: #ffffff;
        border-radius: 5px;
        padding: 10px;
        font-size: 1rem;
    }
    textarea:focus, input:focus {
        border-color: #00b4d8;
        outline: none;
        box-shadow: 0 0 5px rgba(0, 180, 216, 0.3);
    }
    .footer {
        text-align: center;
        font-size: 0.9rem;
        color: #b3d9ff;
        margin-top: 30px;
    }
</style>
"""

components.html(background_css, height=0)

# Streamlit App with Tabs
def ascii_app():
    st.markdown('<div class="container">', unsafe_allow_html=True)

    st.markdown('<h1 class="header">Hybrid Cryptosystem</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtext">Secure your data using Vigenère and Polybius Ciphers. Encrypt and decrypt your text efficiently!</p>',
        unsafe_allow_html=True,
    )

    # Tabs for Encrypt and Decrypt
    tab1, tab2 = st.tabs(["🔒 Encrypt", "🔓 Decrypt"])

    with tab1:  # Encrypt Tab
        st.subheader("Encryption")
        text = st.text_area("Enter Text to Encrypt:", placeholder="Type your message here...")
        vkey = st.text_input("Enter Key 1 (Vigenère):", placeholder="E.g., mysecurekey")
        pkey = st.text_input("Enter Key 2 (Polybius):", placeholder="E.g., polybiuskey")

        if st.button("Encrypt", key="encrypt"):
            if not text or not vkey or not pkey:
                st.error("Please provide all inputs (text, key1, and key2).")
            else:
                try:
                    # Backend Logic for Encryption
                    def vigenere_encrypt(text, key1):
                        # Extend the key to match the length of the text
                        key = (key1 * (len(text) // len(key1) + 1))[:len(text)]
                        # Encrypt using the Vigenère cipher with extended ASCII
                        encrypted = ''.join(chr((ord(char) + ord(k)) % 256) for char, k in zip(text, key))
                        return encrypted

                    def create_polybius_grid(key):
                        # Generate a seed from the key using a hash
                        seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (10**8)
                        
                        # Create a list of all extended ASCII characters
                        all_chars = [chr(i) for i in range(256)]
                        
                        # Shuffle the characters using the seed
                        import random
                        random.seed(seed)
                        random.shuffle(all_chars)
                        
                        # Use the shuffled characters to build the grid
                        unique_chars = ''.join(all_chars)
                        grid = {unique_chars[i]: (i // 16, i % 16) for i in range(len(unique_chars))}
                        return grid

                    def polybius_encrypt(text, grid):
                        # Convert each character to its coordinates in the grid
                        encrypted = ''.join(f"{grid[char][0]:02}{grid[char][1]:02}" for char in text)
                        return encrypted

                    # Encryption Workflow
                    grid = create_polybius_grid(pkey)
                    
                    vigenere_encrypted = vigenere_encrypt(text, vkey)
                    
                    final_encrypted = polybius_encrypt(vigenere_encrypted, grid)
                    
                    st.success(f"Encrypted Text: {final_encrypted}")

                except Exception as e:
                    st.error(f"An error occurred: {e}")

    with tab2:  # Decrypt Tab
        st.subheader("Decryption")
        text = st.text_area("Enter Text to Decrypt:", placeholder="Type the ciphertext here...")
        vkey = st.text_input("Enter Key 1 (Vigenère):", placeholder="E.g., mysecurekey-")
        pkey = st.text_input("Enter Key 2 (Polybius):", placeholder="E.g., polybiuskey-")

        if st.button("Decrypt", key="decrypt"):
            if not text or not vkey or not pkey:
                st.error("Please provide all inputs (text, key1, and key2).")
            else:
                try:
                    # Backend Logic for Decryption
                    def vigenere_decrypt(cipher, key1):
                        key = key1 
                        key = (key * (len(cipher) // len(key) + 1))[:len(cipher)]
                        decrypted = ''.join(chr((ord(char) - ord(k)) % 256) for char, k in zip(cipher, key))
                        return decrypted

                    def create_reverse_polybius_grid(key):
                        # Generate a seed from the key using a hash
                        seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (10**8)
                        
                        # Create a list of all extended ASCII characters
                        all_chars = [chr(i) for i in range(256)]
                        
                        # Shuffle the characters using the seed
                        import random
                        random.seed(seed)
                        random.shuffle(all_chars)
                        
                        # Build the reverse grid from the shuffled characters
                        reverse_grid = {(i // 16, i % 16): all_chars[i] for i in range(len(all_chars))}
                        return reverse_grid

                    def polybius_decrypt(cipher, reverse_grid):
                        
                        pairs = [(int(cipher[i:i+2]), int(cipher[i+2:i+4])) for i in range(0, len(cipher), 4)]
                        decrypted = ''.join(reverse_grid[pair] for pair in pairs)
                        return decrypted
            
                    # Decryption Workflow
                    reverse_grid = create_reverse_polybius_grid(pkey)
                    polybius_decrypted = polybius_decrypt(text, reverse_grid)
                    final_decrypted = vigenere_decrypt(polybius_decrypted, vkey)
                    st.success(f"Decrypted Text: {final_decrypted}")

                except Exception as e:
                    st.error(f"An error occurred: {e}")

    st.markdown(
        '<div class="footer">Created with  using Streamlit</div>',
        unsafe_allow_html=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)
