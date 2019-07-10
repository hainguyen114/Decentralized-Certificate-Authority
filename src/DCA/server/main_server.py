import subprocess
import socket
import os 
import lib.sub_func as fs
import lib.storj as st
from pathlib import Path
path = Path(__file__).resolve().parent.__str__()

if __name__ == "__main__":
        
    BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
    #os.environ["PATH"] = "$HOME/go/bin:$PATH"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.bind((fs.ip_address, int(fs.port_connect)-1))

        a = s.listen(5)
        
        i = 0
        
        server = st.StorjServer()

        print("##########################################################")
        print("--                                                      --")
        print("--       Welcome to DEMO Decentralized CA System        --")
        print("--                                                      --")
        print("##########################################################")
        print('\n')
        print("Server is running...")

    except:
        print("Failed to start server!")
        fs.sys.exit(0)

    while True:
        out = ''
        conn, addr = s.accept()
        print(' address:',addr)
        data = conn.recv(BUFFER_SIZE)
        
        if not data: 
            conn.send(bytes([0]))
            break
        out = out + data.decode('utf-8')
        print(out)
        subprocess.call(['multichain-cli','chaindemo','grant',out,'connect'])
        key = [fs.KEY_STORJ_INFO]
        key.append(out)
        content = {}

        content['access_key'] = server._gateway_access_key
        content['secret_key'] = server._gateway_secret_key
        content['api_key'] = server._gateway_api_key
        content['bucket_name'] = server.generate_bucket_name(out)

        client = st.StorjClient(fs.satellite_addr, content['api_key'], content['access_key'], content['secret_key'])
        client.setup()

        server.make_bucket(content['bucket_name'])

        tx = fs.api.publish(fs.STREAM_STORJKEY,key,{'json':content})
        conn.send(bytes([1]))  # echo
        
        i += 1

        print("The number of nodes in chain: " + str(i))
    conn.close()

