package dev.pocketkeyboard

import android.app.Activity
import android.os.Bundle
import android.content.Context
import android.graphics.Color
import android.text.Editable
import android.text.TextWatcher
import android.view.Gravity
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.View
import android.graphics.drawable.GradientDrawable
import android.view.inputmethod.InputMethodManager
import android.widget.*
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.InetSocketAddress
import java.security.MessageDigest
import java.security.SecureRandom
import java.security.cert.X509Certificate
import java.util.concurrent.LinkedBlockingQueue
import javax.net.ssl.SSLContext
import javax.net.ssl.SSLSocket
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

class MainActivity : Activity() {
    private val prefs by lazy { getSharedPreferences("peer", MODE_PRIVATE) }
    private lateinit var status: TextView
    private lateinit var host: EditText
    private lateinit var code: EditText
    private lateinit var editor: EditText
    private val outgoing = LinkedBlockingQueue<String>(512)
    @Volatile private var running = true
    @Volatile private var ready = false
    @Volatile private var worker: Thread? = null
    private var previous = ""
    private var ignoreEdit = false
    private var connectedSocket: SSLSocket? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val scale = resources.displayMetrics.density
        val pad = (16 * scale).toInt()
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
        }
        val scroll = ScrollView(this)
        scroll.addView(root)
        setContentView(scroll)

        fun heading(s: String) = TextView(this).apply {
            text = s
            textSize = 22f
            setTextColor(Color.BLACK)
            setPadding(0, 0, 0, pad / 2)
            root.addView(this)
        }
        heading("PocketKeyboard")
        status = TextView(this).apply { text = "Not connected"; textSize = 16f; root.addView(this) }
        host = EditText(this).apply {
            hint = "PC address (e.g. 10.0.0.172)"
            setSingleLine(true)
            setText(prefs.getString("host", ""))
            inputType = android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_URI
            root.addView(this)
        }
        code = EditText(this).apply {
            hint = "Pairing code (first connection only)"
            setSingleLine(true)
            inputType = android.text.InputType.TYPE_CLASS_NUMBER
            root.addView(this)
        }
        val buttons = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; root.addView(this) }
        fun button(label: String, parent: LinearLayout = root, callback: () -> Unit) =
            Button(this).apply { text = label; setOnClickListener { callback() }; parent.addView(this) }
        button("Connect", buttons) { startConnection() }
        button("Forget pairing", buttons) {
            prefs.edit().remove("token").remove("pin").apply()
            ready = false
            connectedSocket?.close()
            showStatus("Pairing forgotten. Get a new code from the PC tray icon.")
        }
        val help = TextView(this).apply {
            text = "Type or use your keyboard's microphone. The PC's focused window receives the text. Tap Clear to begin a fresh phone input buffer without deleting PC text."
            setPadding(0, pad, 0, pad / 2)
            root.addView(this)
        }
        editor = EditText(this).apply {
            hint = "Tap here to type on your PC…"
            minLines = 4
            gravity = Gravity.TOP
            inputType = android.text.InputType.TYPE_CLASS_TEXT or
                android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE or
                android.text.InputType.TYPE_TEXT_FLAG_AUTO_CORRECT or
                android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
            isEnabled = false
            root.addView(this)
        }
        editor.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                if (ignoreEdit) return
                val updated = s?.toString() ?: ""
                if (!ready) { previous = updated; return }
                val old = previous
                var prefix = 0
                while (prefix < old.length && prefix < updated.length && old[prefix] == updated[prefix]) prefix++
                var suffix = 0
                while (suffix < old.length - prefix && suffix < updated.length - prefix &&
                    old[old.length - suffix - 1] == updated[updated.length - suffix - 1]) suffix++
                val removed = old.length - prefix - suffix
                val inserted = updated.substring(prefix, updated.length - suffix)
                // Keep the remote caret at the end of the mirrored buffer.
                repeat(suffix) { send(JSONObject().put("type", "key").put("value", "LEFT")) }
                repeat(removed) { send(JSONObject().put("type", "key").put("value", "BACKSPACE")) }
                if (inserted.isNotEmpty()) send(JSONObject().put("type", "text").put("value", inserted))
                repeat(suffix) { send(JSONObject().put("type", "key").put("value", "RIGHT")) }
                previous = updated
            }
        })
        val tools = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; root.addView(this) }
        button("Clear buffer", tools) {
            ignoreEdit = true
            editor.setText("")
            previous = ""
            ignoreEdit = false
            editor.requestFocus()
        }
        // Trackpad uses relative movement; it never steals focus from the PC.
        val title = TextView(this).apply {
            text = "Touchpad  •  tap: click  •  double-tap: double-click  •  hold: right-click"
            textSize = 14f
            setPadding(0, pad, 0, pad / 2)
            root.addView(this)
        }
        val detector = GestureDetector(this, object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent): Boolean = true
            override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
                send(JSONObject().put("type", "mouse_click").put("value", "left"))
                return true
            }
            override fun onDoubleTap(e: MotionEvent): Boolean {
                send(JSONObject().put("type", "mouse_click").put("value", "double"))
                return true
            }
            override fun onLongPress(e: MotionEvent) {
                send(JSONObject().put("type", "mouse_click").put("value", "right"))
            }
            override fun onScroll(e1: MotionEvent?, e2: MotionEvent, distanceX: Float, distanceY: Float): Boolean {
                // GestureDetector distances describe finger movement in inverse directions.
                // Scale from Android dp to a comfortable mouse movement in Windows pixels.
                val dx = (-distanceX / scale * 1.5f).toInt().coerceIn(-300, 300)
                val dy = (-distanceY / scale * 1.5f).toInt().coerceIn(-300, 300)
                if (dx != 0 || dy != 0) send(JSONObject().put("type", "mouse_move").put("dx", dx).put("dy", dy))
                return true
            }
        })
        val touchpad = View(this).apply {
            contentDescription = "PC touchpad. Tap to click, double tap to double click, hold to right click."
            background = GradientDrawable().apply {
                setColor(Color.rgb(226, 233, 241))
                cornerRadius = 14 * scale
                setStroke((1 * scale).toInt().coerceAtLeast(1), Color.rgb(120, 135, 150))
            }
            setOnTouchListener { _, event ->
                detector.onTouchEvent(event)
                true
            }
            root.addView(this, LinearLayout.LayoutParams(-1, (220 * scale).toInt()))
        }
        val quick = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; root.addView(this) }
        fun quickButton(label: String, kind: String, value: String, parent: LinearLayout) {
            Button(this).apply {
                text = label
                setAllCaps(false)
                setOnClickListener { send(JSONObject().put("type", kind).put("value", value)) }
                parent.addView(this, LinearLayout.LayoutParams(0, (52 * scale).toInt(), 1f))
            }
        }
        quickButton("Vol −", "key", "VOLUME_DOWN", quick)
        quickButton("Vol +", "key", "VOLUME_UP", quick)
        quickButton("Mute", "key", "VOLUME_MUTE", quick)
        val editing = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; root.addView(this) }
        quickButton("Copy", "shortcut", "COPY", editing)
        quickButton("All + Copy", "shortcut", "SELECT_ALL_COPY", editing)
        quickButton("Paste", "shortcut", "PASTE", editing)
        val keys = listOf(listOf("Esc" to "ESCAPE", "Tab" to "TAB", "Enter" to "ENTER", "⌫" to "BACKSPACE"),
            listOf("←" to "LEFT", "↑" to "UP", "↓" to "DOWN", "→" to "RIGHT"))
        keys.forEach { row ->
            val bar = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; root.addView(this) }
            row.forEach { (label, key) ->
                Button(this).apply {
                    text = label
                    setOnClickListener { send(JSONObject().put("type", "key").put("value", key)) }
                    bar.addView(this, LinearLayout.LayoutParams(0, (52 * scale).toInt(), 1f))
                }
            }
        }
        if (prefs.getString("token", null) != null && prefs.getString("host", null) != null) startConnection()
    }

    private fun showStatus(message: String) = runOnUiThread {
        status.text = message
        editor.isEnabled = ready
        if (ready) {
            code.visibility = android.view.View.GONE
            editor.requestFocus()
            (getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager)
                .showSoftInput(editor, InputMethodManager.SHOW_IMPLICIT)
        } else code.visibility = android.view.View.VISIBLE
    }

    private fun send(json: JSONObject) {
        if (!ready) return
        if (!outgoing.offer(json.toString())) showStatus("Input buffer full; reconnect before continuing.")
    }

    private fun startConnection() {
        val address = host.text.toString().trim()
        if (address.isEmpty()) { showStatus("Enter the PC's Wi-Fi address"); return }
        prefs.edit().putString("host", address).apply()
        connectedSocket?.close()
        worker?.interrupt()
        outgoing.clear()
        worker = Thread { connectLoop(address, code.text.toString().trim()) }.also { it.start() }
    }

    private fun connectLoop(address: String, initialCode: String) {
        var tries = 0
        while (running && !Thread.currentThread().isInterrupted) {
            ready = false
            showStatus("Connecting to $address…")
            try {
                val trust = object : X509TrustManager {
                    override fun getAcceptedIssuers(): Array<X509Certificate> = emptyArray()
                    override fun checkClientTrusted(chain: Array<X509Certificate>?, authType: String?) {}
                    override fun checkServerTrusted(chain: Array<X509Certificate>?, authType: String?) {
                        if (chain.isNullOrEmpty()) throw java.security.cert.CertificateException("No certificate")
                    }
                }
                val tls = SSLContext.getInstance("TLS")
                tls.init(null, arrayOf<TrustManager>(trust), SecureRandom())
                val socket = tls.socketFactory.createSocket() as SSLSocket
                connectedSocket = socket
                socket.soTimeout = 20000
                socket.connect(InetSocketAddress(address, 38476), 3500)
                socket.startHandshake()
                val actualPin = MessageDigest.getInstance("SHA-256").digest(socket.session.peerCertificates[0].encoded)
                    .joinToString("") { "%02x".format(it) }
                val pinned = prefs.getString("pin", null)
                if (pinned != null && pinned != actualPin) throw SecurityException("PC certificate changed; refusing connection")
                val output = OutputStreamWriter(socket.outputStream, Charsets.UTF_8).buffered()
                val input = BufferedReader(InputStreamReader(socket.inputStream, Charsets.UTF_8))
                val token = prefs.getString("token", null)
                if (token == null) {
                    if (initialCode.length != 6) throw SecurityException("Open Pair a phone on the PC and enter its six-digit code")
                    output.write(JSONObject().put("type", "pair").put("code", initialCode).toString() + "\n")
                } else output.write(JSONObject().put("type", "hello").put("token", token).toString() + "\n")
                output.flush()
                val response = JSONObject(input.readLine() ?: throw Exception("PC closed connection"))
                when (response.optString("type")) {
                    "paired" -> {
                        prefs.edit().putString("token", response.getString("token")).putString("pin", actualPin).apply()
                    }
                    "ready" -> { if (pinned == null) throw SecurityException("Missing saved certificate fingerprint") }
                    else -> throw SecurityException("PC declined pairing or authentication")
                }
                ready = true
                outgoing.clear()
                tries = 0
                showStatus("Connected securely to $address")
                socket.soTimeout = 0
                while (running && !Thread.currentThread().isInterrupted) {
                    val message = outgoing.take()
                    output.write(message + "\n")
                    output.flush()
                }
            } catch (e: Exception) {
                ready = false
                outgoing.clear()
                showStatus("Disconnected: ${e.message ?: "network error"}")
                if (prefs.getString("token", null) == null || e is SecurityException) break
            } finally {
                try { connectedSocket?.close() } catch (_: Exception) {}
            }
            tries++
            try { Thread.sleep(if (tries < 4) 1500 else 4000) } catch (_: InterruptedException) { break }
        }
    }

    override fun onDestroy() {
        running = false
        ready = false
        connectedSocket?.close()
        worker?.interrupt()
        super.onDestroy()
    }
}
