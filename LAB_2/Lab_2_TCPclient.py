import socket

def tcp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_address = ('localhost', 65432)
    client_socket.connect(server_address)
    
    try:
        message = "Сообщение отправленное на сервер"
        print(f"Отправка: {message}")
        client_socket.sendall(message.encode())

        data = client_socket.recv(1024)
        print(f"Ответ от сервера: {data.decode()}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    tcp_client()