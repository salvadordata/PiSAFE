from modules.dsame3.dsame import DSAMEDecoder

def test_decoder():
    decoder = DSAMEDecoder()
    message = "ZCZC-WXR-RWT-020103-020209-020091-020121-029047-029165-029095-029037+0030-1051700-KEAX/NWS"
    decoded_message = decoder.decode(message)
    print("Decoded Message:", decoded_message)

if __name__ == "__main__":
    test_decoder()
