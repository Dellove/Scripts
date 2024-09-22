import socket

def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    server_address = ('localhost', 65433)
    server_socket.bind(server_address)
    print("UDP-сервер ожидает сообщений...")
    
    while True:
        data, client_address = server_socket.recvfrom(1024)
        message = data.decode()
        print(f"Получено сообщение: {message} от {client_address}")
        
        if message.lower() == 'exit':
            print("Закрытие сервера.")
            break
        
        server_socket.sendto(data, client_address)
    
    server_socket.close()
    print("Сервер закрыт.")

if __name__ == "__main__":
    udp_server()
