"""A module that implements a realization of simple http server."""
import os
import socket
import sys
import io
import mimetypes

class MyServer():
    """Simple http requests handler."""
    def __init__(self):
        self.main_dir = os.getcwd()
        print("main_dir:", self.main_dir)

    def send_answer(self, conn, status="200 OK", typ="text/plain; charset=utf-8", data=""):
        """A method for sending data back to client"""
        conn.send(b"HTTP/1.1 " + status.encode("utf-8") + b"\r\n")
        conn.send(b"Server: simplehttp\r\n")
        conn.send(b"Connection: close\r\n")
        conn.send(b"Content-Type: " + typ.encode("utf-8") + b"\r\n")
        conn.send(b"Content-Length: " + bytes(len(data)) + b"\r\n")
        conn.send(b"\r\n")
        conn.send(data)

    def get_req(self, conn):
        """A method that handles get requests from client"""
        data = b""

        while b"\r\n" not in data:
            tmp = conn.recv(1024)
            if not tmp:
                break
            else:
                data += tmp

        if not data:
            return

        udata = data.decode("utf-8")
        udata = udata.split("\r\n", 1)[0]
        print("New request:", udata)
        method, address, _ = udata.split(" ", 2)

        dict_path = os.getcwd()
        files = os.listdir()

        if method == "GET" and "index.html" in files:
            self.open_file("index.html")
            return

        if method == "GET" and os.path.isdir(address[1:]):
            self.list_files(address[1:])
            return

        if method == "GET" and address != "/" and os.path.isfile(address[1:]):
            self.open_file(address[1:])
            return

        self.list_files(dict_path)


    def list_files(self, path):
        """A method for showing all files and directories in given directory"""
        files = os.listdir(path)
        f = io.StringIO()
        f.write("<!DOCTYPE html>\n")
        if path != self.main_dir:
            f.write("<html>\n<title>Listing for %s</title>\n" % path)
            f.write("<body>\n<h1>Listing for %s</h1>\n" % path)
        else:
            f.write("<html>\n<title>Listing for %s</title>\n" % path.split('/')[-1])
            f.write("<body>\n<h1>Listing for %s</h1>\n" % path.split('/')[-1])
        f.write("<hr>\n<ul>\n")
        for name in files:
            if self.main_dir == path:
                f.write('<li><a href="%s">%s</a></li>\n' % (name, name))
            else:
                f.write('<li><a href="%s">%s</a></li>\n' % (path + "/" + name, name))

        f.write("</ul>\n</html>")
        self.send_answer(conn, typ="text/html; charset=utf-8", data=f.getvalue().encode())
        f.close()
        return


    def open_file(self, file):
        """A method for proper opening any kind of files"""

        t = "text/html; charset=utf-8"
        _, ext = os.path.splitext(file)
        if ext in mimetypes.types_map:
            t = mimetypes.types_map[ext]

        file = open(file, 'rb')
        file_read = file.read()
        self.send_answer(conn, typ=t, data=file_read)
        return


if __name__ == '__main__':

    server = MyServer()

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", port))
    s.listen(5)


    try:
        while True:
            conn, addr = s.accept()
            print("New connection from " + addr[0])
            try:
                server.get_req(conn)
            except:
                server.send_answer(conn, "500 Internal Server Error", data=b"Error")
            finally:
                conn.close()
    finally:
        s.close()
