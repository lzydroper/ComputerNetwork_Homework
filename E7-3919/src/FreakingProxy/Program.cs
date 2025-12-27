using System.Net;
using System.Net.Sockets;

long _sessionCnt = 0;
// ==============
// 代理服务器Socket
// ==============
const string LISTEN_IP = "192.168.163.1";
const int LISTEN_PORT = 3919;

Console.WriteLine($"[{DateTime.Now:HH:mm:ss}][Main] Freaking Proxy is starting...");

var serverSocket = new Socket(
    AddressFamily.InterNetwork,
    SocketType.Stream,
    ProtocolType.Tcp
);

serverSocket.Bind(new IPEndPoint(IPAddress.Parse(LISTEN_IP), LISTEN_PORT));
serverSocket.Listen(10);

Console.WriteLine($"[{DateTime.Now:HH:mm:ss}][Main] Listening on {LISTEN_IP}:{LISTEN_PORT}");

// ==============
// 监听客户端接入
// ==============
while (true)
{
    var clientSocket = await serverSocket.AcceptAsync();
    Console.WriteLine($"[{DateTime.Now:HH:mm:ss}][Main] Client connected: {clientSocket.RemoteEndPoint}");

    // 启动一个新线程处理该客户端会话
    _ = Task.Run(() => HandleSessionAsync(clientSocket));
}

// ==============
// 处理客户端会话
// ==============
async Task HandleSessionAsync(Socket clientSocket)
{
    long id = Interlocked.Increment(ref _sessionCnt);
    Socket? remoteSocket = null;
    byte[] reply =
    [
        0x05,       // Socket5
        0x00,       // REP = succeeded
        0x00,       // RSV
        0x01,       // ATYP = IPv4
        0x00, 0x00, 0x00, 0x00, // BND.ADDR:PORT = 0.0.0.0:0，ai说是这样快一点
        0x00, 0x00
    ];

    try
    {
        // 握握手
        var targetSocket = await HandleSocketAsync(clientSocket);
        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}][S#{id:D2}] Target = {targetSocket.ip}:{targetSocket.port}");

        // 释放忍术
        remoteSocket = new Socket(
            AddressFamily.InterNetwork,
            SocketType.Stream,
            ProtocolType.Tcp
        );
        await remoteSocket.ConnectAsync(targetSocket.ip, targetSocket.port);
        await clientSocket.SendAsync(reply, SocketFlags.None);

        // 双向转发
        await RelayAsync(clientSocket, remoteSocket);
    }
    catch (Exception e)
    {
        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}][S#{id:D2}] Error: {e.Message}");
    }
    finally
    {
        try { clientSocket.Shutdown(SocketShutdown.Both); } catch { }
        try { remoteSocket?.Shutdown(SocketShutdown.Both); } catch { }
        clientSocket.Close();
        remoteSocket?.Close();

        Console.WriteLine($"[{DateTime.Now:HH:mm:ss}][S#{id:D2}] Closed");
    }
}

async Task<(string ip, int port)> HandleSocketAsync(Socket clientSocket)
{
    byte[] buffer = new byte[256];

    // 方法协商，Socket5，无认证
    await clientSocket.ReceiveAsync(buffer, SocketFlags.None);
    if (buffer[0] != 0x05)
        throw new Exception("Not Socket5");
    await clientSocket.SendAsync(new byte[] { 0x05, 0x00 }, SocketFlags.None);

    // 请求连接，只处理域名（哪有人ip看网页）
    await clientSocket.ReceiveAsync(buffer, SocketFlags.None);
    if (buffer[1] != 0x01)
        throw new Exception("Not CONNECT");

    byte atyp = buffer[3];
    int index = 4;
    string ip;

    if (atyp == 0x03)
    {
        int domainLen = buffer[index++];
        ip = System.Text.Encoding.ASCII.GetString(buffer, index, domainLen);
        index += domainLen;
    }
    else
    {
        throw new Exception("Only Do Domain");
    }

    int port = (buffer[index] << 8) | buffer[index + 1];
    return (ip, port);
}

async Task RelayAsync(Socket clientSocket, Socket remoteSocket)
{
    var task1 = ForwardAsync(clientSocket, remoteSocket);
    var task2 = ForwardAsync(remoteSocket, clientSocket);
    await Task.WhenAny(task1, task2);
}

async Task ForwardAsync(Socket fromSocket, Socket toSocket)
{
    byte[] buffer = new byte[8196];

    while (true)
    {
        int bytesRead = await fromSocket.ReceiveAsync(buffer, SocketFlags.None);
        if (bytesRead <= 0)
            break;
        await toSocket.SendAsync(
            new ArraySegment<byte>(buffer, 0, bytesRead),
            SocketFlags.None
        );
    }
}