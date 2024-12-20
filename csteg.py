from PIL import Image
import random
import os
import streamlit as st
import hashlib
# Function to embed data into an image
def embed_data_into_image(image_path, data, output_path):
    # Open the image
    img = Image.open(image_path)
    img = img.convert("RGB")  # Ensure it's in RGB mode
    pixels = img.load()
    
    # Convert the data to binary
    binary_data = ''.join(format(ord(char), '08b') for char in data)
    binary_data += '1111111111111110'  # End of data marker
    
    data_index = 0
    width, height = img.size
    
    # Loop through the pixels to embed the data
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            if data_index < len(binary_data):
                r = (r & ~1) | int(binary_data[data_index])  # Modify LSB of red
                data_index += 1
            if data_index < len(binary_data):
                g = (g & ~1) | int(binary_data[data_index])  # Modify LSB of green
                data_index += 1
            if data_index < len(binary_data):
                b = (b & ~1) | int(binary_data[data_index])  # Modify LSB of blue
                data_index += 1
            
            pixels[x, y] = (r, g, b)
            
            if data_index >= len(binary_data):
                break
        if data_index >= len(binary_data):
            break
    
    # Save the modified image
    img.save(output_path)
    return output_path

# Function to select a random image from a folder
def get_random_image(folder):
    images = [file for file in os.listdir(folder) if file.endswith(('png', 'jpg', 'jpeg'))]
    return os.path.join(folder, random.choice(images))
"""
def extract_data_from_image(image_path):
    # Open the image
    img = Image.open(image_path)
    img = img.convert("RGB")
    pixels = img.load()
    
    binary_data = ""
    width, height = img.size
    
    # Loop through pixels to extract data
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)  # Extract LSB of red
            binary_data += str(g & 1)  # Extract LSB of green
            binary_data += str(b & 1)  # Extract LSB of blue
            
    # Split binary data at the end of data marker
    binary_data = binary_data.split('1111111111111110')[0]
    
    # Convert binary to string
    data = ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))
    return data
"""
def extract_data_from_image(image_path):
    from PIL import Image
    
    # Open the image
    img = Image.open(image_path)
    img = img.convert("RGB")
    pixels = img.load()
    print(image_path)
    binary_data = ""
    width, height = img.size
    print("imhere")
    # Loop through pixels to extract data
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            binary_data += str(r & 1)  # Extract LSB of red
            binary_data += str(g & 1)  # Extract LSB of green
            binary_data += str(b & 1)  # Extract LSB of blue
    print("comp for)")
    # Look for the end marker ('1111111111111110')
    end_marker = '1111111111111110'
    if end_marker in binary_data:
        binary_data = binary_data.split(end_marker)[0]  # Extract data before the end marker
    else:
        raise ValueError("End marker not found in the image data.")
    
    # Ensure the binary data length is a multiple of 8 for proper conversion
    if len(binary_data) % 8 != 0:
        raise ValueError("Corrupted data: Binary length is not a multiple of 8.")
    
    # Convert binary data to a string
    data = ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))
    return data
def steg():
    st.title("HYBRID CRYPTOSYSTEM TO SECURE Message in Image")
    tab1, tab2 = st.tabs(["🔒 Encrypt", "🔓 Decrypt"])

    import os
    import random
    import streamlit as sti
    from stegano import lsb
    import hashlib

    def get_random_image(folder):
        """Fetch a random image from the given folder."""
        images = [f for f in os.listdir(folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not images:
            raise FileNotFoundError("No images found in the specified folder.")
        return os.path.join(folder, random.choice(images))

    # Streamlit App
    with tab1:  # Encrypt Tab
        st.subheader("Encryption")
        text = sti.text_area("Enter Text to Encrypt:", placeholder="Type your message here...")
        vkey = sti.text_input("Enter Key 1 (Vigenère):", placeholder="E.g., mysecurekey")
        pkey = sti.text_input("Enter Key 2 (Polybius):", placeholder="E.g., polybiuskey")

        if sti.button("Encrypt", key="encrypt"):
            if not text or not vkey or not pkey:
                sti.error("Please provide all inputs (text, key1, and key2).")
            else:
                try:
                    # Vigenère Cipher
                    def vigenere_encrypt(text, key1):
                        key = (key1 * (len(text) // len(key1) + 1))[:len(text)]
                        encrypted = ''.join(chr((ord(char) + ord(k)) % 256) for char, k in zip(text, key))
                        return encrypted

                    # Polybius Cipher
                    def create_polybius_grid(key):
                        seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (10**8)
                        all_chars = [chr(i) for i in range(256)]
                        random.seed(seed)
                        random.shuffle(all_chars)
                        unique_chars = ''.join(all_chars)
                        grid = {unique_chars[i]: (i // 16, i % 16) for i in range(len(unique_chars))}
                        return grid

                    def polybius_encrypt(text, grid):
                        encrypted = ''.join(f"{grid[char][0]:02}{grid[char][1]:02}" for char in text)
                        return encrypted

                    # Workflow
                    polybius_grid = create_polybius_grid(pkey)
                    vigenere_encrypted = vigenere_encrypt(text, vkey)
                    final_encrypted = polybius_encrypt(vigenere_encrypted, polybius_grid)

                    # Random Image Selection and Embedding
                    random_folder = "random"  # Path to the folder with random images
                    encoded_folder = "encoded"  # Path to save encoded images

                    os.makedirs(encoded_folder, exist_ok=True)  # Ensure the encoded folder exists

                    random_image_path = get_random_image(random_folder)
                    encoded_image_path = os.path.join(encoded_folder, "encoded_image.png")

                    # Embed data into the selected image
                    lsb.hide(random_image_path, final_encrypted).save(encoded_image_path)

                    # Display and allow download
                    sti.image(encoded_image_path, caption="Image with Embedded Data")
                    sti.success("Data successfully embedded into the image.")

                    with open(encoded_image_path, "rb") as file:
                        sti.download_button(
                            label="Download Encoded Image",
                            data=file,
                            file_name="encoded_image.png",
                            mime="image/png"
                        )
                except Exception as e:
                    sti.error(f"An error occurred: {e}")

    with tab2:  # Decrypt Tab
        sti.subheader("Decryption")
        
        uploaded_image = sti.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])
        vkey = st.text_input("Enter Key 1 (Vigenère):", placeholder="E.g., mysecurekey-")
        pkey = st.text_input("Enter Key 2 (Polybius):", placeholder="E.g., polybiuskey-")

        if sti.button("Decrypt", key="decrypt"):
            if not uploaded_image or not vkey or not pkey:
                sti.error("Please provide all inputs (image, key1, and key2).")
            else:
                try:
                    # Vigenère Decryption
                    def vigenere_decrypt(cipher, key1):
                        key = (key1 * (len(cipher) // len(key1) + 1))[:len(cipher)]
                        decrypted = ''.join(chr((ord(char) - ord(k)) % 256) for char, k in zip(cipher, key))
                        return decrypted

                    # Reverse Polybius Grid Creation
                    def create_reverse_polybius_grid(key):
                        seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (10**8)
                        all_chars = [chr(i) for i in range(256)]
                        import random
                        random.seed(seed)
                        random.shuffle(all_chars)
                        reverse_grid = {(i // 16, i % 16): all_chars[i] for i in range(len(all_chars))}
                        return reverse_grid

                    # Polybius Decryption
                    def polybius_decrypt(cipher, reverse_grid):
                        pairs = [(int(cipher[i:i+2]), int(cipher[i+2:i+4])) for i in range(0, len(cipher), 4)]
                        decrypted = ''.join(reverse_grid[pair] for pair in pairs)
                        return decrypted

                    # Save uploaded image temporarily
                    input_image_path = f"uploaded_{uploaded_image.name}"
                    with open(input_image_path, "wb") as f:
                        f.write(uploaded_image.read())

                    # Extract data from the image
                    from stegano import lsb
                    extracted_data = lsb.reveal(input_image_path)
                    if not extracted_data:
                        st.error("No hidden message found in the uploaded image.")
                        raise ValueError("Extraction failed: No hidden message.")

                    # Decrypt the extracted data
                    reverse_grid = create_reverse_polybius_grid(pkey)
                    decrypted_polybius = polybius_decrypt(extracted_data, reverse_grid)
                    original_text = vigenere_decrypt(decrypted_polybius, vkey)

                    # Display the decrypted message
                    sti.success(f"Decrypted Text: {original_text}")

                except Exception as e:
                    sti.error(f"An error occurred during decryption: {e}")

