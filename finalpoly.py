
from PIL import Image
import binascii
import imageio.v2 as imageio  # updated for the latest imageio version
import os
import sys
from shutil import rmtree

four_k = (3840, 2160)
HD = (1920, 1080)

def make_gif(parent_folder, fname):
    items = os.listdir(parent_folder)
    png_filenames = [elem for elem in items if elem.endswith(".png")]

    sorted_png = sorted(
        png_filenames,
        key=lambda p: int(p.split("-")[1].split(".")[0])
    )

    with imageio.get_writer(f"{fname}.gif", mode="I", duration=0.8) as writer:
        for filename in sorted_png:
            image = imageio.imread(os.path.join(parent_folder, filename))
            writer.append_data(image)
    return f"{fname}.gif"

def pixels_2_png(pixels, fname, reso=four_k):
    img = Image.new("RGB", reso)
    img.putdata(pixels)
    img.save(fname)
    print(f"pixels_2_png: Saved {len(pixels)} pixels to {fname}")

def png_2_pixels(fname):
    with Image.open(fname) as im:
        pixel_list = list(im.getdata())
    print(f"png_2_pixels: Read {len(pixel_list)} pixels from {fname}")
    return pixel_list

def bits_2_file(bits, fname):
    with open(fname, "wb") as f:
        for idx in range(0, len(bits), 8):
            byte = bits[idx:idx + 8]
            f.write(int("".join(byte), 2).to_bytes(1, "big"))

def file_2_bits(fname):
    bits = []
    with open(fname, "rb") as f:
        byte = f.read(1)
        while byte:
            bits.extend(bin(ord(byte))[2:].zfill(8))
            byte = f.read(1)
    return bits

def bits_2_pixels(bits):
    pixels = [(0, 0, 0) if b == "0" else (255, 255, 255) for b in bits]
    print(f"bits_2_pixels: Converted {len(bits)} bits to {len(pixels)} pixels")
    return pixels

def pixels_2_bits(pixels):
    bits = ["0" if p == (0, 0, 0) else "1" for p in pixels]
    print(f"pixels_2_bits: Converted {len(pixels)} pixels to {len(bits)} bits")
    return bits

def add_header(bits, fname):
    fname_bitstr = bin(int(binascii.hexlify(fname.encode()), 16))[2:]
    fname_bitstr_length_bitstr = bin(len(fname_bitstr))[2:].zfill(16)
    payload_length_header = bin(len(bits))[2:].zfill(64)
    header_list = list(fname_bitstr_length_bitstr + fname_bitstr + payload_length_header)
    return header_list + bits


import re

def decode_header(bits):
    def decode_binary_string(s):
        try:
            return ''.join(chr(int(s[i * 8:i * 8 + 8], 2)) for i in range(len(s) // 8))
        except ValueError:
            return None

    fname_length = int(''.join(bits[:16]), 2)
    fname_bits = ''.join(bits[16:16 + fname_length])
    payload_length = int(''.join(bits[16 + fname_length:16 + fname_length + 64]), 2)

    # Decode the file name and handle decoding errors
    fname = decode_binary_string(fname_bits)
    if not fname:
        fname = "default_name"
    
    # Sanitize the filename by keeping only alphanumeric characters, underscores, and dots
    fname = re.sub(r'[^A-Za-z0-9_.]', '_', fname)

    return fname, bits[16 + fname_length + 64:16 + fname_length + 64 + payload_length]

def polybius_decipher(encrypted_data, key):
    # Create a dictionary mapping key characters to binary pairs
    cipher_map = {}
    for i, char in enumerate(key):
        binary_pair = format(i, '08b')  # Convert index to binary
        cipher_map[char] = binary_pair

    # Decrypt data
    decrypted_data = ''
    for char in encrypted_data:
        decrypted_data += cipher_map.get(char, '')

    # Remove padding
    decrypted_data = decrypted_data.rstrip('0')

    return decrypted_data

def decode(src,binary_key,pkey,ext):
    def iter_frames(im):
        try:
            i = 0
            while True:
                im.seek(i)
                yield im.convert("RGB")
                i += 1
        except EOFError:
            pass

    pixels = []
    with Image.open(src) as im:
        for frame in iter_frames(im):
            pixels.extend(list(frame.getdata()))
    
    bits = pixels_2_bits(pixels)
    grid, grid_chars = create_polybius_grid(pkey)

    bits = polybius_decrypt(bits,grid,grid_chars)
    bits = binary_vigenere_decrypt(bits,binary_key)
    #bits=polybius_cipher_binary_reverse(bits)
    fname, bits = decode_header(bits)

    # Ensure the recovered file name has its original extension (or defaults to .bin)
    if '.' in fname:
        recovered_fname = f"recovered_files/{fname.split('.')[0]}-recovered.{fname.split('.')[-1]}"
    else:
        recovered_fname = f"recovered_files/{fname}-recovered.bin"  # Default to .bin if no extension

    # Ensure the folder exists before saving
    os.makedirs("recovered_files", exist_ok=True)

    # Save the recovered file in its original format
    bits_2_file(bits, recovered_fname)
    convert_bin_to_format("recovered_files","recovered_files",ext)



def test_bit_similarity(bits1, bits2):
    if len(bits1) != len(bits2):
        print("Bit lengths are not the same!")
        return
    for b1, b2 in zip(bits1, bits2):
        if b1 != b2:
            print("Bits are not the same!")
            return
    print("Bits are identical")

def clear_folder(relative_path):
    try:
        rmtree(relative_path)
    except FileNotFoundError:
        print("WARNING: Could not locate /temp directory.")
    os.makedirs(relative_path, exist_ok=True)
def polybius_cipher_binary(data):
    # Define Polybius cipher square for binary data
    polybius_square = {
        "00": "11", "01": "10", "10": "01", "11": "00"
    }
    
    # Initialize encrypted data string
    encrypted_data = ""
    
    # Loop through the binary data in pairs of 2 bits
    for i in range(0, len(data) - 1, 2):  # Process in steps of 2 (no padding)
        pair = ''.join(data[i:i+2])  # Convert the list to a string
        encrypted_data += polybius_square.get(pair, "")
    
    # Return the encrypted binary data
    return encrypted_data

def polybius_cipher_binary_reverse(encrypted_data):
    # Define the reverse Polybius cipher square for binary data
    reverse_polybius_square = {
        "00": "11", "01": "10", "10": "01", "11": "00"
    }
    
    # Initialize the decrypted data string
    decrypted_data = ""
    
    # Loop through the encrypted data in chunks of 2 bits
    for i in range(0, len(encrypted_data), 2):
        pair = ''.join(encrypted_data[i:i+2])  # Convert the list to a string
        decrypted_data += reverse_polybius_square.get(pair, "")
    
    # Return the decrypted binary data
    return decrypted_data

def binary_vigenere_encrypt(data, key):
    # Repeat the key to match the length of the data
    repeated_key = (key * (len(data) // len(key) + 1))[:len(data)]
    
    # Perform XOR between data and repeated key
    encrypted_data = ''.join(
        str(int(bit) ^ int(repeated_key[i])) for i, bit in enumerate(data)
    )   
    return encrypted_data

def binary_vigenere_decrypt(encrypted_data, key):
    # Repeat the key to match the length of the encrypted data
    repeated_key = (key * (len(encrypted_data) // len(key) + 1))[:len(encrypted_data)]
    
    # Perform XOR between encrypted data and repeated key
    decrypted_data = ''.join(
        str(int(bit) ^ int(repeated_key[i])) for i, bit in enumerate(encrypted_data)
    )
    
    return decrypted_data
"""
def create_polybius_grid(key):
    # Ensure key is unique by removing duplicates
    unique_key = ''.join(sorted(set(key), key=key.index))
    
    # Generate a list of characters that will fill the grid
    all_chars = ''.join(chr(i) for i in range(256))
    
    # Remove characters that are already in the key
    remaining_chars = ''.join([c for c in all_chars if c not in unique_key])
    
    # The final grid will be the key followed by the remaining characters
    grid_chars = unique_key + remaining_chars
    
    # Create the Polybius grid (6x6)
    grid = {}
    for i in range(256):
        # Get 6-bit binary representation
        row = f"{i // 16:04b}"  # Top 4 bits for the row
        col = f"{i % 16:04b}"  # Bottom 4 bits for the column
        grid[grid_chars[i]] = (row, col)  # Store the row and column
    return grid, grid_chars

def polybius_encrypt(binary_input, grid):
    encrypted = []
    # Encrypt by finding the corresponding row and column for each 8-bit chunk
    for i in range(0, len(binary_input), 8):
        byte = binary_input[i:i+8]
        if len(byte) == 8:  # Only encrypt if the byte is exactly 8 bits
            char = chr(int(byte, 2))
            if char in grid:
                row, col = grid[char]
                encrypted.append(row + col)
        else:  # For less than 8 bits, add it directly to encrypted output
            encrypted.append(byte)
    return ''.join(encrypted)

def polybius_decrypt(binary_cipher, grid, grid_chars):
    # Reverse the grid for decryption
    inverse_grid = {row + col: char for char, (row, col) in grid.items()}
    decrypted = []
    # Decrypt the binary cipher by extracting the corresponding character
    for i in range(0, len(binary_cipher), 8):
        pair = binary_cipher[i:i+8]
        if pair in inverse_grid:
            decrypted.append(inverse_grid[pair])
        else:  # For less than 8 bits, add them directly to decrypted output
            decrypted.append(pair)
    
    # Convert decrypted binary back to the original text
    return ''.join([f"{ord(c):08b}" for c in decrypted])
"""
#grid, grid_chars = create_polybius_grid(key)
"""
# Input binary data as a string
binary_input = "0100100001100101011011000110110001101111"  # Binary for "Hello"
print(f"Binary Input: {binary_input}")

# Encrypt the binary input
encrypted = polybius_encrypt(binary_input, grid)
print(f"Encrypted Binary: {encrypted}")

# Decrypt the binary cipher back to original binary
decrypted = polybius_decrypt(encrypted, grid, grid_chars)
print(f"Decrypted Binary: {decrypted}")

# Convert the decrypted binary back to text for verification (if needed)
text_output = ''.join(chr(int(decrypted[i:i+8], 2)) for i in range(0, len(decrypted), 8))
print(f"Decrypted Text: {text_output}")

"""
def create_polybius_grid(key):
    # Ensure key is unique by removing duplicates
    unique_key = ''.join(sorted(set(key), key=key.index))
    
    # Generate a list of characters that will fill the grid
    all_chars = ''.join(chr(i) for i in range(256))
    
    # Remove characters that are already in the key
    remaining_chars = ''.join([c for c in all_chars if c not in unique_key])
    
    # The final grid will be the key followed by the remaining characters
    grid_chars = unique_key + remaining_chars
    
    # Create the Polybius grid (16x16 for extended ASCII)
    grid = {}
    for i in range(256):
        # Get 8-bit binary representation for row and column
        row = f"{i // 16:04b}"  # Top 4 bits for the row
        col = f"{i % 16:04b}"  # Bottom 4 bits for the column
        grid[grid_chars[i]] = row + col  # Concatenate row and col as a string (not a tuple)
    return grid, grid_chars

def polybius_encrypt(binary_input, grid):
    encrypted = []
    # Encrypt by finding the corresponding row and column for each 8-bit chunk
    for i in range(0, len(binary_input), 8):
        byte = binary_input[i:i+8]
        if len(byte) == 8:  # Only encrypt if the byte is exactly 8 bits
            char = chr(int(byte, 2))  # Convert byte (binary) to character
            if char in grid:
                encrypted.append(grid[char])  # Append the row + col directly from the grid
        else:  # For less than 8 bits, add them directly to encrypted output
            encrypted.append(byte)
    return ''.join(encrypted)

def polybius_decrypt(binary_cipher, grid, grid_chars):
    # Reverse the grid for decryption (use concatenated row + col as key)
    inverse_grid = {v: k for k, v in grid.items()}  # Flip grid to map row+col -> char
    decrypted = []

    # Ensure binary_cipher is a string (not a list)
    if isinstance(binary_cipher, list):
        binary_cipher = ''.join(binary_cipher)  # If it's a list, convert to string

    # Decrypt the binary cipher by extracting the corresponding character
    for i in range(0, len(binary_cipher), 8):
        pair = binary_cipher[i:i+8]
        if len(pair) == 8:  # Ensure that each "pair" is 8 bits
            if pair in inverse_grid:  # Check for the concatenated string pair as the key
                decrypted.append(inverse_grid[pair])  # Append the matched character
            else:  # If pair doesn't match, add it directly
                decrypted.append(pair)
        else:  # For cases with less than 8 bits, handle accordingly
            decrypted.append(pair)
    
    # Convert decrypted characters back to binary
    decrypted_binary = ''.join([f"{ord(c):08b}" for c in decrypted])

    return decrypted_binary

"""
def polybius_decrypt(binary_cipher, grid,grid_chars):
    decrypted = []

    # Iterate through the ciphered binary input in 8-bit chunks
    for i in range(0, len(binary_cipher), 8):
        pair = binary_cipher[i:i+8]  # Extract 8-bit pair
        for char, code in grid.items():
            if code == pair:  # Check if pair matches any code in the grid
                decrypted.append(char)  # Append matched character
                break
        else:
            # If no match, treat it as an unmatched binary code
            decrypted.append(pair)  # Append the unmatched binary pair as a string

    # Join the list into a string and return the decrypted text
    decrypted_string = ''.join(decrypted)

    return decrypted_string
"""
# gemini

# Example usage


# Example usage

# Example usage


# Example usage

def encode(src,key,pkey, res):
    bits = file_2_bits(src)
    bits = add_header(bits, os.path.basename(src))
    
    #bits =  polybius_cipher_binary(bits)
    grid, grid_chars = create_polybius_grid(pkey)
    bits = binary_vigenere_encrypt(bits,key)

    bits = polybius_encrypt(bits,grid)
    pixels = bits_2_pixels(bits)
    pixels_per_image = res[0] * res[1]
    num_imgs = (len(pixels) + pixels_per_image - 1) // pixels_per_image
    clear_folder("temp")
    for i in range(num_imgs):
        cur_temp_name = f"temp/{os.path.basename(src)}-{i}.png"
        cur_start_idx = i * pixels_per_image
        cur_pixels = pixels[cur_start_idx:cur_start_idx + pixels_per_image]
        pixels_2_png(cur_pixels, cur_temp_name)
    return make_gif("temp", os.path.basename(src))


def conversion_test():
    src_f = "data/test.jpg"
    img_f = "data/image.png"
    test_f_bits = add_header(file_2_bits(src_f), os.path.basename(src_f))
    pixels = bits_2_pixels(test_f_bits)
    pixels_2_png(pixels, img_f)
    pixels = png_2_pixels(img_f)
    bits = pixels_2_bits(pixels)
    fname, bits = decode_header(bits)
    bits_2_file(bits, f"{src_f.split('.')[0]}-copy.{src_f.split('.')[1]}")
    test_bit_similarity(file_2_bits(src_f), bits)

import os

def convert_all_bin_to_jpg(input_folder, output_folder="recovered"):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        # Check if the file has a .bin extension
        if filename.endswith(".bin"):
            bin_file_path = os.path.join(input_folder, filename)

            # Read binary data from the .bin file
            with open(bin_file_path, 'rb') as bin_file:
                binary_data = bin_file.read()

            # Set output path for the .jpg file
            jpg_file_name = os.path.splitext(filename)[0] + ".jpg"
            jpg_file_path = os.path.join(output_folder, jpg_file_name)

            # Write the binary data to the new .jpg file
            with open(jpg_file_path, 'wb') as jpg_file:
                jpg_file.write(binary_data)

            print(f"Converted {bin_file_path} to {jpg_file_path}")

import os

def convert_bin_to_format(input_folder, output_folder="recovered", output_extension="jpg"):
    """
    Converts .bin files in the input folder to a specified format and saves them in the output folder.
    
    Parameters:
        input_folder (str): Path to the folder containing .bin files.
        output_folder (str): Path to the folder where converted files will be saved.
        output_extension (str): The desired output file extension (e.g., 'jpg', 'png', 'txt', 'mp3').
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".bin"):
            bin_file_path = os.path.join(input_folder, filename)

            # Read binary data from the .bin file
            with open(bin_file_path, 'rb') as bin_file:
                binary_data = bin_file.read()

            # Set the output file path with the new extension
            output_file_name = os.path.splitext(filename)[0] + f".{output_extension.lower()}"
            output_file_path = os.path.join(output_folder, output_file_name)

            # Handle specific extensions
            if output_extension.lower() in ["jpg", "png", "mp3"]:
                # Save binary data directly for these formats
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(binary_data)
            elif output_extension.lower() == "txt":
                # Decode binary data to text for .txt files
                with open(output_file_path, 'w', encoding="utf-8", errors='replace') as output_file:
                    output_file.write(binary_data.decode(errors='replace'))
            else:
                raise ValueError(f"Unsupported file extension: {output_extension}")

            print(f"Converted {bin_file_path} to {output_file_path}")

# Example usage

"""def main():
    #encode("data/test.mp3")
    #decode("test.mp3.gif")

    #encode("data/test.txt")
    #decode("test.txt.gif")
    
    #encode("data/test.jpg")
    decode("test.jpg.gif")
    input_folder = "recovered_files"
    convert_all_bin_to_jpg(input_folder)
if __name__ == "__main__":
    main()

"""
