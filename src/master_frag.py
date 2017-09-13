import sys
import base64
import cryptographics


# test reassembly
def reassemble_frags(ordered_frags):
    reassembly_bytes = b''
    for frag in ordered_frags:
        print(len(frag))
        reassembly_bytes += frag

    return reassembly_bytes


# create and append a SHA256 HMAC for authentication
def HMAC(cipher_piece, seqID, secret_key):
    cat_input = bytes((secret_key + seqID).encode('utf-8'))
    hmac = cryptographics.SHA256(cat_input)
    ciph_n_hash = cipher_piece + hmac.encode('utf-8')
    #print("ciph_n_hash: {} ({}) length: {}".format(ciph_n_hash, type(ciph_n_hash), len(ciph_n_hash)))
    return ciph_n_hash


# encrypt a piece
def encrypt_piece(piece, secret_key):
    crypt = cryptographics.AESCipher(secret_key)
    cipher_piece = crypt.encrypt(str(piece))

    return cipher_piece


# prepare pieces to be distributed via encryption and HMAC
def prepare_pieces(pieces, secret_key):
    secured_pieces = []
    for i in range(0, len(pieces)):
        cipher_piece = encrypt_piece(pieces[i], secret_key)
        ciph_n_hash = HMAC(cipher_piece, str(i), secret_key)
        secured_pieces.append(ciph_n_hash)

    return secured_pieces


# split byte array into n equal-sized pieces
def subdivide_file(file_bytes, n):
    total_size = len(file_bytes)
    frag_size = (total_size - (total_size % n)) / n
    pieces = []
    pieces.append(b'')
    i = 0 # iterator position in string
    p = 1 # current piece
    while i < len(file_bytes):
        if p < n and i >= frag_size * p:
            pieces.append(file_bytes[i:(i+1)])
            p+=1
        else:
            pieces[p-1] += file_bytes[i:(i+1)]
        i+=1

    return pieces

# target file into binary string
def read_in_file(path_to_orig_file):
    with open(path_to_orig_file, 'r+b') as f:
        file_bytes = f.read()
    # must delete file after splitting
    f.close()

    return file_bytes


def output_fragments(fragments):
    for frag in fragments:
        fpath = 'OUT_FOLDER/' + cryptographics.generate_key(8)
        with open(fpath, 'wb') as f:
            f.write(frag)
        f.close()

# main controller loop
def demo(argv):
    # arguments
    path = argv[1]
    n = int(argv[2])
    secret_key = cryptographics.generate_key(16)
    # read in file
    file_bytes = read_in_file(path)
    # fragment
    file_pieces = subdivide_file(file_bytes, n)
    # reassemble test
    fragments = prepare_pieces(file_pieces, secret_key)

    for piece in fragments:
        print('\n{}'.format(piece))

    output_fragments(fragments)


def validate_arguments(argv):
    # check for correct commandline arguments before advancing to demo logic
    if len(argv) != 3:
        print("Incorrect number of arguments. Format:")
        print("<path_to_file_to_frag> <number_of_fragments>")
        exit()
    elif len(argv) == 3:
        try:
            int(argv[2])
        except ValueError:
            print("Incorrect type of arguments. Format:")
            print("<(string) path_to_file_to_frag> <(int) number_of_fragments>")
    demo(argv)


if __name__ == "__main__":
    validate_arguments(sys.argv)
    