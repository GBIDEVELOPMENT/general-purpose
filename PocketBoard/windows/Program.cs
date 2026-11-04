using System.Net;
using System.Net.Security;
using System.Net.Sockets;
using System.Net.NetworkInformation;
using System.Security.Authentication;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Text.Json;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using System.Drawing;

namespace PocketKeyboard;

internal static class Program
{
    [STAThread]
    static void Main()
    {
        using var singleton = new Mutex(true, "Local\\PocketKeyboard.TrayReceiver", out var firstInstance);
        if (!firstInstance) return;
        ApplicationConfiguration.Initialize();
        using var instance = new TrayServer();
        Application.Run(instance);
    }
}

internal sealed class TrayServer : ApplicationContext
{
    const int Port = 38476;
    const int DiscoveryPort = 38477;
    readonly string dataDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PocketKeyboard");
    readonly NotifyIcon tray;
    readonly ToolStripMenuItem toggle;
    readonly CancellationTokenSource shutdown = new();
    readonly HashSet<string> tokens = new(StringComparer.Ordinal);
    readonly object sync = new();
    TcpListener? listener;
    UdpClient? discovery;
    X509Certificate2 certificate;

    int revocationEpoch;
    volatile bool enabled = true;

    public TrayServer()
    {
        Directory.CreateDirectory(dataDir);
        var certPath = Path.Combine(dataDir, "server.pfx");
        if (File.Exists(certPath)) certificate = new X509Certificate2(certPath, "", X509KeyStorageFlags.Exportable);
        else
        {
            using var key = RSA.Create(2048);
            var request = new CertificateRequest("CN=PocketBoard", key, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
            request.CertificateExtensions.Add(new X509BasicConstraintsExtension(false, false, 0, false));
            request.CertificateExtensions.Add(new X509KeyUsageExtension(X509KeyUsageFlags.DigitalSignature | X509KeyUsageFlags.KeyEncipherment, false));
            using var generated = request.CreateSelfSigned(DateTimeOffset.UtcNow.AddDays(-1), DateTimeOffset.UtcNow.AddYears(10));
            certificate = new X509Certificate2(generated.Export(X509ContentType.Pfx, ""), "", X509KeyStorageFlags.Exportable);
            File.WriteAllBytes(certPath, certificate.Export(X509ContentType.Pfx, ""));
        }
        var tokenFile = Path.Combine(dataDir, "tokens.txt");
        if (File.Exists(tokenFile))
            foreach (var line in File.ReadAllLines(tokenFile))
                if (line.Length == 64) tokens.Add(line);

        toggle = new ToolStripMenuItem("Pause receiving", null, (_, _) => Toggle());
        var menu = new ContextMenuStrip();
        menu.Items.Add(new ToolStripMenuItem("PocketBoard: running", null) { Enabled = false, Name = "state" });
        menu.Items.Add(toggle);
        menu.Items.Add(new ToolStripMenuItem("Show network details", null, (_, _) => ShowNetwork()));
        menu.Items.Add(new ToolStripMenuItem("Forget all paired phones", null, (_, _) => Revoke()));
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add(new ToolStripMenuItem("Exit", null, (_, _) => ExitThread()));
        tray = new NotifyIcon
        {
            Icon = SystemIcons.Information,
            Text = "PocketBoard: running",
            Visible = true,
            ContextMenuStrip = menu
        };
        tray.DoubleClick += (_, _) => ShowNetwork();
        listener = new TcpListener(IPAddress.Any, Port);
        try
        {
            listener.Start();
            _ = AcceptLoop();
            discovery = new UdpClient(new IPEndPoint(IPAddress.Any, DiscoveryPort));
            _ = DiscoveryLoop();
        }
        catch (Exception e)
        {
            MessageBox.Show("Cannot listen on TCP " + Port + ": " + e.Message, "PocketBoard");
            tray.Text = "PocketBoard: not listening";
        }
    }

    void Toggle()
    {
        enabled = !enabled;
        if (!enabled) InputInjector.ReleaseAltTab();
        toggle.Text = enabled ? "Pause receiving" : "Resume receiving";
        tray.Text = enabled ? "PocketBoard: running" : "PocketBoard: paused";
        tray.Icon = enabled ? SystemIcons.Information : SystemIcons.Warning;
        tray.ContextMenuStrip!.Items["state"]!.Text = enabled ? "PocketBoard: running" : "PocketBoard: paused";
    }

    void ShowNetwork()
    {
        var addresses = Dns.GetHostAddresses(Dns.GetHostName())
            .Where(a => a.AddressFamily == AddressFamily.InterNetwork && !IPAddress.IsLoopback(a)).Select(a => a.ToString());
        MessageBox.Show("On your phone, choose Discover and select this PC.\n\n" +
            Environment.MachineName + "\nAddresses: " + string.Join(", ", addresses) +
            "\nTCP: " + Port + "   Discovery UDP: " + DiscoveryPort +
            "\n\nAny device on the local subnet can connect while the receiver is enabled. Pause receiving when unused.", "PocketBoard");
    }

    // Discovery never exposes tokens. Only clients on an actual local interface's
    // IPv4 subnet receive a response, and auto-enrollment uses the same restriction.
    static bool OnLocalSubnet(IPAddress address)
    {
        if (address.AddressFamily != AddressFamily.InterNetwork) return false;
        var bytes = address.GetAddressBytes();
        foreach (var adapter in NetworkInterface.GetAllNetworkInterfaces())
        {
            if (adapter.OperationalStatus != OperationalStatus.Up ||
                adapter.NetworkInterfaceType == NetworkInterfaceType.Loopback) continue;
            foreach (var unicast in adapter.GetIPProperties().UnicastAddresses)
            {
                if (unicast.Address.AddressFamily != AddressFamily.InterNetwork ||
                    unicast.IPv4Mask is null) continue;
                var own = unicast.Address.GetAddressBytes();
                var mask = unicast.IPv4Mask.GetAddressBytes();
                if (mask.All(b => b == 255)) continue; // excludes /32 overlay tunnel endpoints
                if (Enumerable.Range(0, 4).All(i => (bytes[i] & mask[i]) == (own[i] & mask[i]))) return true;
            }
        }
        return false;
    }

    async Task DiscoveryLoop()
    {
        while (!shutdown.IsCancellationRequested)
        {
            try
            {
                var packet = await discovery!.ReceiveAsync(shutdown.Token);
                if (!enabled || !OnLocalSubnet(packet.RemoteEndPoint.Address) ||
                    Encoding.ASCII.GetString(packet.Buffer) != "POCKETKEYBOARD_DISCOVER_V1") continue;
                var data = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(new {
                    type = "pocketkeyboard_pc", name = Environment.MachineName,
                    address = packet.RemoteEndPoint.Address.ToString(), port = Port
                }));
                // The client uses the UDP source address, not the echoed address.
                await discovery.SendAsync(data, packet.RemoteEndPoint, shutdown.Token);
            }
            catch (OperationCanceledException) { break; }
            catch (ObjectDisposedException) { break; }
            catch (Exception) { await Task.Delay(150); }
        }
    }

    void Revoke()
    {
        if (MessageBox.Show("Disconnect and revoke all previously paired phones?", "PocketBoard", MessageBoxButtons.YesNo) != DialogResult.Yes) return;
        lock (sync)
        {
            revocationEpoch++;
            InputInjector.ReleaseAltTab();
            tokens.Clear();
            File.WriteAllText(Path.Combine(dataDir, "tokens.txt"), "");
        }
        MessageBox.Show("Paired-phone tokens revoked. Existing connections must reconnect to take effect.", "PocketBoard");
    }

    async Task AcceptLoop()
    {
        while (!shutdown.IsCancellationRequested)
        {
            try
            {
                var client = await listener!.AcceptTcpClientAsync(shutdown.Token);
                _ = Handle(client);
            }
            catch (OperationCanceledException) { break; }
            catch (ObjectDisposedException) { break; }
            catch { await Task.Delay(250); }
        }
    }

    async Task Handle(TcpClient client)
    {
        using (client)
        {
            client.ReceiveTimeout = 20000;
            client.SendTimeout = 20000;
            using var tls = new SslStream(client.GetStream(), false);
            try
            {
                await tls.AuthenticateAsServerAsync(new SslServerAuthenticationOptions
                {
                    ServerCertificate = certificate,
                    EnabledSslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13
                }, shutdown.Token);
                using var reader = new StreamReader(tls, Encoding.UTF8, false, 4096, true);
                using var writer = new StreamWriter(tls, new UTF8Encoding(false), 4096, true) { AutoFlush = true };
                var first = await reader.ReadLineAsync(shutdown.Token);
                if (first is null || first.Length > 4096) return;
                using var intro = JsonDocument.Parse(first);
                var kind = Get(intro.RootElement, "type");
                bool authenticated = false;
                if (kind == "enroll" || kind == "pair")
                {
                    string? token = null;
                    lock (sync)
                    {
                        if (enabled && OnLocalSubnet(((IPEndPoint)client.Client.RemoteEndPoint!).Address))
                        {
                            token = Convert.ToHexString(RandomNumberGenerator.GetBytes(32));
                            tokens.Add(token);
                            File.WriteAllLines(Path.Combine(dataDir, "tokens.txt"), tokens);
                        }
                    }
                    if (token != null)
                    {
                        await writer.WriteLineAsync(JsonSerializer.Serialize(new { type = "paired", token }));
                        authenticated = true;
                    }
                    else await writer.WriteLineAsync("{\"type\":\"denied\"}");
                }
                else if (kind == "hello")
                {
                    lock (sync) authenticated = enabled && tokens.Contains(Get(intro.RootElement, "token"));
                    await writer.WriteLineAsync(authenticated ? "{\"type\":\"ready\"}" : "{\"type\":\"denied\"}");
                }
                if (!authenticated) return;
                int epoch;
                lock (sync) epoch = revocationEpoch;
                while (!shutdown.IsCancellationRequested)
                {
                    var line = await reader.ReadLineAsync(shutdown.Token);
                    if (line is null) break;
                    if (line.Length > 8192) break;
                    lock (sync)
                    {
                        if (!enabled || epoch != revocationEpoch) break;
                    }
                    using var msg = JsonDocument.Parse(line);
                    var root = msg.RootElement;
                    switch (Get(root, "type"))
                    {
                        case "text": InputInjector.Text(Get(root, "value", 4096)); break;
                        case "key": InputInjector.Key(Get(root, "value", 30)); break;
                        case "shortcut": InputInjector.Shortcut(Get(root, "value", 30)); break;
                        case "mouse_click": InputInjector.MouseClick(Get(root, "value", 20)); break;
                        case "mouse_move":
                            int dx = root.TryGetProperty("dx", out var mx) && mx.TryGetInt32(out var x) ? Math.Clamp(x, -300, 300) : 0;
                            int dy = root.TryGetProperty("dy", out var my) && my.TryGetInt32(out var y) ? Math.Clamp(y, -300, 300) : 0;
                            InputInjector.MouseMove(dx, dy);
                            break;
                        case "replace":
                            int count = root.TryGetProperty("delete", out var num) && num.TryGetInt32(out var n) ? Math.Clamp(n, 0, 4096) : 0;
                            for (int i = 0; i < count; i++) InputInjector.Key("BACKSPACE");
                            InputInjector.Text(Get(root, "text", 4096));
                            break;
                    }
                }
            }
            catch (Exception ex) when (ex is IOException or AuthenticationException or JsonException or SocketException or OperationCanceledException) { }
        }
    }

    static string Get(JsonElement obj, string name, int limit = 256) =>
        obj.ValueKind == JsonValueKind.Object && obj.TryGetProperty(name, out var value) &&
        value.ValueKind == JsonValueKind.String ? (value.GetString() ?? "")[..Math.Min(value.GetString()!.Length, limit)] : "";

    protected override void ExitThreadCore()
    {
        shutdown.Cancel();
        InputInjector.ReleaseAltTab();
        listener?.Stop();
        discovery?.Dispose();
        tray.Visible = false;
        tray.Dispose();
        certificate.Dispose();
        base.ExitThreadCore();
    }
}

internal static class InputInjector
{
    const int KEYEVENTF_KEYUP = 0x0002;
    const int KEYEVENTF_UNICODE = 0x0004;
    const int INPUT_KEYBOARD = 1;
    [StructLayout(LayoutKind.Sequential)]
    struct INPUT { public uint type; public INPUTUNION u; }
    [StructLayout(LayoutKind.Explicit)]
    struct INPUTUNION { [FieldOffset(0)] public KEYBDINPUT ki; [FieldOffset(0)] public MOUSEINPUT mi; }
    [StructLayout(LayoutKind.Sequential)]
    struct MOUSEINPUT { public int dx, dy; public uint mouseData, dwFlags, time; public IntPtr dwExtraInfo; }
    [StructLayout(LayoutKind.Sequential)]
    struct KEYBDINPUT { public ushort wVk, wScan; public uint dwFlags, time; public IntPtr dwExtraInfo; }
    [DllImport("user32.dll", SetLastError = true)] static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
    static void Send(ushort vk, ushort scan, uint flags)
    {
        var inputs = new[] { new INPUT { type = INPUT_KEYBOARD, u = new INPUTUNION { ki = new KEYBDINPUT { wVk = vk, wScan = scan, dwFlags = flags } } } };
        SendInput(1, inputs, Marshal.SizeOf<INPUT>());
    }
    public static void Text(string text)
    {
        foreach (char ch in text)
        {
            Send(0, ch, KEYEVENTF_UNICODE);
            Send(0, ch, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP);
        }
    }
    static readonly object altSync = new();
    static bool altHeld;
    static long altSession;
    public static void AltTab(string action)
    {
        lock (altSync)
        {
            if (action == "ALT_TAB_CLOSE")
            {
                ReleaseAltTab();
                return;
            }
            if (!altHeld)
            {
                Send(0x12, 0, 0); // Alt held while the app switcher is visible
                altHeld = true;
            }
            Send(0x09, 0, 0);
            Send(0x09, 0, KEYEVENTF_KEYUP);
            var session = ++altSession;
            _ = Task.Run(async () =>
            {
                await Task.Delay(12000);
                lock (altSync) if (session == altSession) ReleaseAltTab();
            });
        }
    }
    public static void ReleaseAltTab()
    {
        lock (altSync)
        {
            ++altSession;
            if (!altHeld) return;
            altHeld = false;
            Send(0x12, 0, KEYEVENTF_KEYUP);
        }
    }
    // Keyboard shortcuts are transmitted as *intent*, not arbitrary modifier state.
    // Release Ctrl even when a send fails, avoiding a stuck modifier on the PC.
    public static void Shortcut(string action)
    {
        ushort key = action switch
        {
            "COPY" => 0x43,
            "PASTE" => 0x56,
            "SELECT_ALL_COPY" => 0x43,
            _ => 0
        };
        if (action is "ALT_TAB" or "ALT_TAB_OPEN" or "ALT_TAB_NEXT" or "ALT_TAB_CLOSE")
        {
            AltTab(action == "ALT_TAB" ? "ALT_TAB_OPEN" : action);
            return;
        }
        if (key == 0) return;
        Send(0x11, 0, 0); // Ctrl down
        try
        {
            if (action == "SELECT_ALL_COPY")
            {
                Send(0x41, 0, 0); // A
                Send(0x41, 0, KEYEVENTF_KEYUP);
            }
            Send(key, 0, 0);
            Send(key, 0, KEYEVENTF_KEYUP);
        }
        finally { Send(0x11, 0, KEYEVENTF_KEYUP); }
    }
    const uint MOUSEEVENTF_MOVE = 0x0001;
    const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    const uint MOUSEEVENTF_LEFTUP = 0x0004;
    const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    const uint MOUSEEVENTF_RIGHTUP = 0x0010;
    static void Mouse(uint flags, int dx = 0, int dy = 0)
    {
        var inputs = new[] { new INPUT { type = 0, u = new INPUTUNION
        {
            mi = new MOUSEINPUT { dx = dx, dy = dy, dwFlags = flags }
        } } };
        SendInput(1, inputs, Marshal.SizeOf<INPUT>());
    }
    public static void MouseMove(int dx, int dy)
    {
        if (dx != 0 || dy != 0) Mouse(MOUSEEVENTF_MOVE, dx, dy);
    }
    public static void MouseClick(string action)
    {
        if (action == "right")
        {
            Mouse(MOUSEEVENTF_RIGHTDOWN);
            Mouse(MOUSEEVENTF_RIGHTUP);
        }
        else if (action is "left" or "double")
        {
            int count = action == "double" ? 2 : 1;
            for (int i = 0; i < count; i++)
            {
                Mouse(MOUSEEVENTF_LEFTDOWN);
                Mouse(MOUSEEVENTF_LEFTUP);
            }
        }
    }

    public static void Key(string key)
    {
        ushort vk = key switch
        {
            "BACKSPACE" => 0x08, "ENTER" => 0x0D, "TAB" => 0x09,
            "ESCAPE" => 0x1B, "LEFT" => 0x25, "UP" => 0x26,
            "RIGHT" => 0x27, "DOWN" => 0x28, "DELETE" => 0x2E,
            "VOLUME_UP" => 0xAF, "VOLUME_DOWN" => 0xAE, "VOLUME_MUTE" => 0xAD,
            _ => 0
        };
        if (vk == 0) return;
        Send(vk, 0, 0);
        Send(vk, 0, KEYEVENTF_KEYUP);
    }
}
