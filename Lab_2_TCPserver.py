import socket

def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 65432)
    server_socket.bind(server_address)

    server_socket.listen(1)
    print("TCP-сервер ожидает подключения...")

    connection, client_address = server_socket.accept()
    print(f"Подключен клиент: {client_address}")

    try:
        while True:
            data = connection.recv(1024)
            if data:
                print(f"Получено сообщение: {data.decode()}")
                connection.sendall(data)
            else:
                break
    finally:
        connection.close()
        print("Соединение закрыто")

if __name__ == "__main__":
    tcp_server()


