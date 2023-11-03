import os
import socket
import threading

IP = input("Enter your address:")
PORT = 8000
SIZE = 1024
FORMAT = "utf"
UPLOAD_FOLDER = "upload_folder"
DOWNLOAD_FOLDER = "upload_folder"

print("[STARTING] Server is starting.\n")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))
server.listen()
print("[LISTENING] Server is waiting for clients.")

def handleConnection(conn):
    def upload(conn):
        def uploadFile(fileName):
            """ Sending files """
            files = sorted(os.listdir(UPLOAD_FOLDER))

            for file_name in files:
                if(file_name == fileName):
                    """ Send the file name """
                    msg = f"FILENAME:{file_name}"
                    print(f"[SERVER] Uploading the filename: {file_name}")
                    conn.send(msg.encode(FORMAT))

                    """ Recv the reply from the server """
                    msg = conn.recv(SIZE).decode(FORMAT)
                    print(f"[CLIENT] {msg}")

                    """ Send the data """
                    file = open(os.path.join(UPLOAD_FOLDER, file_name), "r")
                    file_data = file.read()

                    msg = f"DATA:{file_data}"
                    conn.send(msg.encode(FORMAT))
                    msg = conn.recv(SIZE).decode(FORMAT)
                    print(f"[CLIENT] {msg}")

                    """ Sending the close command """
                    msg = f"FINISH:Completed data send"
                    conn.send(msg.encode(FORMAT))
                    msg = conn.recv(SIZE).decode(FORMAT)
                    print(f"[CLIENT] {msg}")

                    """ Closing the connection from the server """
                    msg = f"CLOSE:File transfer complete"
                    conn.send(msg.encode(FORMAT))
        
        filelistsend = ""
        filelist = sorted(os.listdir(UPLOAD_FOLDER))
        for i in filelist:
            filelistsend = filelistsend + i + "|"
        filelistsend = filelistsend[:-1]
        print(filelistsend)
        conn.send(filelistsend.encode(FORMAT))
        fileName = conn.recv(SIZE).decode(FORMAT)
        uploadFile(fileName)

    def download(conn):
        """ Receiving files """
        while True:
            msg = conn.recv(SIZE).decode(FORMAT)
            cmd, data = msg.split(":")

            if cmd == "FILENAME":
                """ Recv the file name """
                print(f"[SERVER] Downloaded the filename: {data}.")

                file_path = os.path.join(DOWNLOAD_FOLDER, data)
                file = open(file_path, "w")
                conn.send("Filename uploaded".encode(FORMAT))

            elif cmd == "DATA":
                """ Recv data from client """
                print(f"[SERVER] downloading the file data.")
                file.write(data)
                conn.send("File data uploaded".encode(FORMAT))

            elif cmd == "FINISH":
                file.close()
                print(f"[CLIENT] {data}.\n")
                conn.send("The data is saved.".encode(FORMAT))

            elif cmd == "CLOSE":
                print(f"[CLIENT] {data}")
                break

    while True:
        choice = conn.recv(SIZE).decode(FORMAT)
        if(choice == "upload"):
            download(conn)
        elif(choice == "download"):
            upload(conn)
        elif(choice == "exit"):
            conn.close()
            break

while True:
    conn, addr = server.accept()
    print(f"[NEW CONNECTION] {addr} connected.\n")
    threading.Thread(target=handleConnection, args=(conn,)).start()