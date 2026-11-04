using System.Net;
using System.Net.Security;
using System.Net.Sockets;
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
        ApplicationConfiguration.Initialize();
        using var instance = new TrayServer();
        Application.Run(instance);
    }
}

internal sealed class TrayServer : ApplicationContext
{
    const int Port = 38476;
    readonly string dataDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PocketKeyboard");
    readonly NotifyIcon tray;
    readonly ToolStripMenuItem toggle;
    readonly CancellationTokenSource shutdown = new();
    readonly HashSet<string> tokens = new(StringComparer.Ordinal);
    readonly object sync = new();
    TcpListener? listener;
    X509Certificate2 certificate;
    string? pairingCode;
    DateTime pairingExpires;
    int pairingFailures;
    volatile bool enabled = true;

    public TrayServer()
    {
        Directory.CreateDirectory(dataDir);
        var certPath = Path.Combine(dataDir, "server.pfx");
        if (File.Exists(certPath)) certificate = new X509Certificate2(certPath, "", X509KeyStorageFlags.Exportable);
        else
        {
            using var key = RSA.Create(2048);
            var request = new CertificateRequest("CN=PocketKeyboard", key, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
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
        menu.Items.Add(new ToolStripMenuItem("PocketKeyboard: running", null) { Enabled = false, Name = "state" });
        menu.Items.Add(toggle);
        menu.Items.Add(new ToolStripMenuItem("Pair a phone...", null, (_, _) => ShowPairing()));
        menu.Items.Add(new ToolStripMenuItem("Forget all paired phones", null, (_, _) => Revoke()));
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add(new ToolStripMenuItem("Exit", null, (_, _) => ExitThread()));
        tray = new NotifyIcon
        {
            Icon = SystemIcons.Information,
            Text = "PocketKeyboard: running",
            Visible = true,
            ContextMenuStrip = menu
        };
        tray.DoubleClick += (_, _) => ShowPairing();
        listener = new TcpListener(IPAddress.Any, Port);
        try
        {
            listener.Start();
            _ = AcceptLoop();
        }
        catch (Exception e)
        {
            MessageBox.Show("Cannot listen on TCP " + Port + ": " + e.Message, "PocketKeyboard");
            tray.Text = "PocketKeyboard: not listening";
        }
    }

    void Toggle()
    {
        enabled = !enabled;
        toggle.Text = enabled ? "Pause receiving" : "Resume receiving";
        tray.Text = enabled ? "PocketKeyboard: running" : "PocketKeyboard: paused";
        tray.Icon = enabled ? SystemIcons.Information : SystemIcons.Warning;
        tray.ContextMenuStrip!.Items["state"]!.Text = enabled ? "PocketKeyboard: running" : "PocketKeyboard: paused";
    }

    void ShowPairing()
    {
        if (!enabled) { MessageBox.Show("Resume receiving before pairing.", "PocketKeyboard"); return; }
        lock (sync)
        {
            pairingCode = RandomNumberGenerator.GetInt32(0, 1_000_000).ToString("D6");
            pairingExpires = DateTime.UtcNow.AddMinutes(3);
            pairingFailures = 0;
        }
        var addresses = Dns.GetHostAddresses(Dns.GetHostName())
            .Where(a => a.AddressFamily == AddressFamily.InterNetwork && !IPAddress.IsLoopback(a)).Select(a => a.ToString());
        MessageBox.Show("On your phone, enter the PC's local address and pairing code.\n\nAddresses: " +
            string.Join(", ", addresses) + "\nPort: " + Port + "\nPairing code: " + pairingCode +
            "\n\nValid for 3 minutes. Only pair on a trusted network.", "Pair PocketKeyboard");
    }

    void Revoke()
    {
        if (MessageBox.Show("Disconnect and revoke all previously paired phones?", "PocketKeyboard", MessageBoxButtons.YesNo) != DialogResult.Yes) return;
        lock (sync)
        {
            tokens.Clear();
            File.WriteAllText(Path.Combine(dataDir, "tokens.txt"), "");
        }
        MessageBox.Show("Paired-phone tokens revoked. Existing connections must reconnect to take effect.", "PocketKeyboard");
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
                if (kind == "pair")
                {
                    var code = Get(intro.RootElement, "code");
                    string? token = null;
                    lock (sync)
                    {
                        if (enabled && pairingCode != null && DateTime.UtcNow < pairingExpires && pairingFailures < 5)
                        {
                            if (code == pairingCode)
                            {
                                token = Convert.ToHexString(RandomNumberGenerator.GetBytes(32));
                                tokens.Add(token);
                                File.WriteAllLines(Path.Combine(dataDir, "tokens.txt"), tokens);
                                pairingCode = null;
                            }
                            else pairingFailures++;
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
                while (!shutdown.IsCancellationRequested)
                {
                    var line = await reader.ReadLineAsync(shutdown.Token);
                    if (line is null) break;
                    if (line.Length > 8192) break;
                    lock (sync)
                    {
                        if (!enabled) break;
                    }
                    using var msg = JsonDocument.Parse(line);
                    var root = msg.RootElement;
                    switch (Get(root, "type"))
                    {
                        case "text": InputInjector.Text(Get(root, "value", 4096)); break;
                        case "key": InputInjector.Key(Get(root, "value", 30)); break;
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
        listener?.Stop();
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
    public static void Key(string key)
    {
        ushort vk = key switch
        {
            "BACKSPACE" => 0x08, "ENTER" => 0x0D, "TAB" => 0x09,
            "ESCAPE" => 0x1B, "LEFT" => 0x25, "UP" => 0x26,
            "RIGHT" => 0x27, "DOWN" => 0x28, "DELETE" => 0x2E,
            _ => 0
        };
        if (vk == 0) return;
        Send(vk, 0, 0);
        Send(vk, 0, KEYEVENTF_KEYUP);
    }
}