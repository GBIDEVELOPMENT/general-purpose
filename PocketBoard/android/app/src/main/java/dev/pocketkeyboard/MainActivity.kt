package dev.pocketkeyboard

import android.app.Activity
import android.os.Bundle
import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.RippleDrawable
import android.content.res.ColorStateList
import android.text.SpannableString
import android.text.style.ForegroundColorSpan
import android.widget.ImageView
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import android.os.Handler
import android.os.Looper
import android.net.wifi.WifiManager
import android.content.DialogInterface
import android.view.WindowManager
import android.view.WindowInsets
import android.os.Build
import android.util.TypedValue
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.SocketTimeoutException
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
    private lateinit var discoveryButton: Button
    private lateinit var touchpadFeedback: TextView
    private lateinit var host: EditText
    private lateinit var editor: EditText
    private val outgoing = LinkedBlockingQueue<String>(512)
    @Volatile private var running = true
    @Volatile private var ready = false
    @Volatile private var worker: Thread? = null
    private var previous = ""
    private var ignoreEdit = false
    private var connectedSocket: SSLSocket? = null
    private var lastConnectedHost = ""
    private var firstReady = false

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()
    private fun bg(color: Int, radius: Int = 12) = GradientDrawable().apply {
        setColor(color)
        cornerRadius = dp(radius).toFloat()
    }
    private fun sendAction(type: String, value: String) =
        send(JSONObject().put("type", type).put("value", value))

    // Flat color, rounded geometry and a restrained press ripple: no gradients,
    // borders, state-list elevation or faux directional lighting.
    private fun flatButton(color: Int, radius: Int = 14): android.graphics.drawable.Drawable =
        RippleDrawable(ColorStateList.valueOf(0x33FFFFFF), bg(color, radius), null)

    private fun circularButton(color: Int): android.graphics.drawable.Drawable {
        val disk = GradientDrawable().apply {
            shape = GradientDrawable.OVAL
            setColor(color)
        }
        return RippleDrawable(ColorStateList.valueOf(0x33FFFFFF), disk, null)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
        window.statusBarColor = Color.rgb(18, 19, 22)
        window.navigationBarColor = Color.rgb(18, 19, 22)
        val charcoal = 0xFF171923.toInt()
        val panel = 0xFF343C58.toInt()
        val white = 0xFFF7F7FF.toInt()
        val accent = 0xFF8CF6B3.toInt()
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(10), dp(4), dp(10), dp(3))
            setBackgroundColor(charcoal)
            isFocusableInTouchMode = true
        }
        setContentView(root)
        // Android 15+ enforces edge-to-edge for target SDK 35. The system clock
        // and notification icons occupy the transparent status-bar inset, so
        // reserve that space above every interactive control. Keep the existing
        // IME handling as well, with no magic fixed status-bar height.
        var lastTopInset = -1
        var lastBottomInset = -1
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            root.setOnApplyWindowInsetsListener { view, insets ->
                val systemBars = insets.getInsets(WindowInsets.Type.systemBars() or WindowInsets.Type.displayCutout())
                val top = if (Build.VERSION.SDK_INT >= 35) systemBars.top else 0
                val bottom = if (insets.isVisible(WindowInsets.Type.ime()))
                    insets.getInsets(WindowInsets.Type.ime()).bottom
                else systemBars.bottom
                if (lastTopInset != top || lastBottomInset != bottom) {
                    lastTopInset = top
                    lastBottomInset = bottom
                    view.setPadding(dp(10), dp(4) + top, dp(10), dp(3) + bottom)
                }
                insets
            }
            root.requestApplyInsets()
        }
        val top = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            root.addView(this, LinearLayout.LayoutParams(-1, dp(41)))
        }
        ImageView(this).apply {
            setImageResource(R.drawable.ic_launcher_art)
            contentDescription = "PocketBoard rainbow keyboard logo"
            top.addView(this, LinearLayout.LayoutParams(dp(32), dp(32)).apply { rightMargin = dp(7) })
        }
        TextView(this).apply {
            val name = SpannableString("PocketBoard ✦")
            val shades = intArrayOf(0xFFFF618D.toInt(), 0xFFFFBA35.toInt(), 0xFF5DCE93.toInt(),
                0xFF50AFFF.toInt(), 0xFFB47BFF.toInt())
            for (i in 6 until 11) name.setSpan(ForegroundColorSpan(shades[i - 6]), i, i + 1, 0)
            name.setSpan(ForegroundColorSpan(0xFFFFCD57.toInt()), 12, 13, 0)
            text = name
            textSize = 18f
            setTypeface(null, Typeface.BOLD)
            setTextColor(white)
            gravity = Gravity.CENTER_VERTICAL
            setSingleLine(true)
            top.addView(this, LinearLayout.LayoutParams(0, dp(36), 1f))
        }
        discoveryButton = Button(this).apply {
            text = "⌁ Discover"
            setAllCaps(false)
            textSize = 12f
            setTextColor(white)
            background = flatButton(0xFF7944D7.toInt(), 20)
            elevation = 0f
            stateListAnimator = null
            setPadding(0, 0, 0, 0)
            setOnClickListener { discover() }
            top.addView(this, LinearLayout.LayoutParams(dp(105), dp(37)))
        }
        status = TextView(this).apply {
            text = "●  Tap Discover to find your PC"
            textSize = 11.5f
            setTextColor(0xFFDDE8FF.toInt())
            gravity = Gravity.CENTER_VERTICAL
            maxLines = 1
            ellipsize = android.text.TextUtils.TruncateAt.END
            setPadding(dp(10), 0, dp(8), 0)
            background = bg(0xFF283040.toInt(), 14)
            root.addView(this, LinearLayout.LayoutParams(-1, dp(26)).apply {
                topMargin = dp(2); bottomMargin = dp(4)
            })
        }
        host = EditText(this).apply {
            setText(prefs.getString("host", ""))
            visibility = View.GONE
            root.addView(this, LinearLayout.LayoutParams(1, 1))
        }
        // Dedicated trackpad consumes its own gesture stream, with no scrolling parent.
        // Calibration from Pixel usage: a full-width swipe previously moved the
        // Windows cursor approximately one-third of the screen. Triple the
        // previous 1.5 dp-scaled gain, while carrying fractional subpixel motion
        // so slow/short gestures are not lost to integer truncation.
        val pointerGain = 4.5f
        var remainderX = 0f
        var remainderY = 0f
        val detector = GestureDetector(this, object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent): Boolean = true
            override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
                sendAction("mouse_click", "left")
                touchpadFeedback.text = "Click"
                return true
            }
            override fun onDoubleTap(e: MotionEvent): Boolean {
                sendAction("mouse_click", "double")
                touchpadFeedback.text = "Double-click"
                return true
            }
            override fun onLongPress(e: MotionEvent) {
                sendAction("mouse_click", "right")
                touchpadFeedback.text = "Right-click"
            }
            override fun onScroll(e1: MotionEvent?, e2: MotionEvent, distanceX: Float, distanceY: Float): Boolean {
                val density = resources.displayMetrics.density
                val rawX = -distanceX / density * pointerGain + remainderX
                val rawY = -distanceY / density * pointerGain + remainderY
                val dx = rawX.toInt().coerceIn(-300, 300)
                val dy = rawY.toInt().coerceIn(-300, 300)
                remainderX = if (rawX > 300f || rawX < -300f) 0f else rawX - dx
                remainderY = if (rawY > 300f || rawY < -300f) 0f else rawY - dy
                if (dx != 0 || dy != 0) {
                    send(JSONObject().put("type", "mouse_move").put("dx", dx).put("dy", dy))
                    touchpadFeedback.text = "Pointer"
                }
                return true
            }
        })
        val trackpad = RainbowPad(this).apply {
            contentDescription = "Rainbow touchpad. Slide to move pointer, tap to click, hold to right-click"
            setOnTouchListener { _, event -> detector.onTouchEvent(event); true }
        }
        val trackpadParams = LinearLayout.LayoutParams(-1, dp(125)).apply {
            topMargin = dp(3)
            bottomMargin = dp(2)
        }
        root.addView(trackpad, trackpadParams)
        touchpadFeedback = TextView(this).apply {
            text = "▧  Pointer · tap / double-tap / hold"
            setTextColor(0xFFDDE1F4.toInt())
            textSize = 11f
            root.addView(this, LinearLayout.LayoutParams(-1, dp(16)))
        }
        val inputBar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            background = bg(0xFF2E3551.toInt(), 13)
            root.addView(this, LinearLayout.LayoutParams(-1, dp(41)).apply { bottomMargin = dp(3) })
        }
        editor = EditText(this).apply {
            hint = "Type or dictate on the PC"
            setHintTextColor(0xFFABB5CD.toInt())
            setTextColor(white)
            textSize = 16f
            setSingleLine(false)
            maxLines = 2
            inputType = android.text.InputType.TYPE_CLASS_TEXT or
                android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE or
                android.text.InputType.TYPE_TEXT_FLAG_AUTO_CORRECT or
                android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
            background = null
            setPadding(dp(12), dp(2), 0, dp(2))
            isEnabled = false
            inputBar.addView(this, LinearLayout.LayoutParams(0, dp(41), 1f))
        }
        // The input field owns Clear and Dictation.
        fun inputAction(name: String, iconRes: Int, color: Int, action: () -> Unit) {
            ImageView(this).apply {
                setImageResource(iconRes)
                setPadding(dp(8), dp(8), dp(8), dp(8))
                background = circularButton(color)
                contentDescription = name
                isClickable = true
                isFocusable = true
                setOnClickListener { action() }
                inputBar.addView(this, LinearLayout.LayoutParams(dp(38), dp(38)).apply { rightMargin = dp(4) })
            }
        }
        inputAction("Clear text input", R.drawable.pb_clear, 0xFFEF4A85.toInt()) {
            sendAction("local", "CLEAR")
        }
        inputAction("Open keyboard for voice dictation", R.drawable.pb_mic, 0xFF8149D6.toInt()) {
            editor.requestFocus()
            (getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager)
                .showSoftInput(editor, InputMethodManager.SHOW_IMPLICIT)
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
                repeat(suffix) { sendAction("key", "LEFT") }
                repeat(removed) { sendAction("key", "BACKSPACE") }
                if (inserted.isNotEmpty()) sendAction("text", inserted)
                repeat(suffix) { sendAction("key", "RIGHT") }
                previous = updated
            }
        })
        val palettes = listOf(
            0xFF46B9FF to 0xFF2666E8, 0xFF00D1D5 to 0xFF069AA4,
            0xFFFB66A3 to 0xFFD82678, 0xFFB481FF to 0xFF7339DF,
            0xFFFFB64A to 0xFFED7027, 0xFFFFE35B to 0xFFE8AF10,
            0xFF44E573 to 0xFF0DB74E, 0xFF4FC6FF to 0xFF2877DC,
            0xFF847CFF to 0xFF5145D6, 0xFFFF76B3 to 0xFFE0397F,
            0xFFB782FF to 0xFF7646D1, 0xFF38DBD7 to 0xFF079BAC,
            0xFF5AE56E to 0xFF15AE45, 0xFFFF7287 to 0xFFD73561
        )
        var buttonIndex = 0
        var showingPause = false // presentation-only: no media state queries
        fun resourceFor(value: String): Int? = when (value) {
            "MEDIA_PREV" -> R.drawable.pb_media_prev
            "MEDIA_NEXT" -> R.drawable.pb_media_next
            "MEDIA_PLAY_PAUSE" -> R.drawable.pb_media_play
            "COPY" -> R.drawable.pb_copy
            "SELECT_ALL_COPY" -> R.drawable.pb_all_copy
            "PASTE" -> R.drawable.pb_paste
            "TAB" -> R.drawable.pb_tab
            "ENTER" -> R.drawable.pb_enter
            "BACKSPACE" -> R.drawable.pb_backspace
            else -> null
        }
        fun controlRow(actions: List<Triple<String, String, String>>) {
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
                root.addView(this, LinearLayout.LayoutParams(-1, dp(53)).apply { topMargin = dp(3) })
            }
            actions.forEach { (title, type, value) ->
                val colors = palettes[(buttonIndex++) % palettes.size]
                val slot = FrameLayout(this).apply {
                    row.addView(this, LinearLayout.LayoutParams(0, dp(52), 1f))
                }
                val circle = FrameLayout(this).apply {
                    background = circularButton(colors.second.toInt())
                    contentDescription = title
                    isFocusable = true
                    isClickable = true
                    slot.addView(this, FrameLayout.LayoutParams(dp(49), dp(49), Gravity.CENTER))
                }
                val symbol = resourceFor(value)
                val icon: ImageView? = if (symbol != null) ImageView(this).apply {
                    setImageResource(symbol)
                    setPadding(dp(9), dp(9), dp(9), dp(9))
                    circle.addView(this, FrameLayout.LayoutParams(-1, -1))
                } else null
                if (icon == null) {
                    val label = when (value) {
                        "ESCAPE" -> "Esc"
                        "VOLUME_DOWN" -> "−"
                        "VOLUME_UP" -> "+"
                        "VOLUME_MUTE" -> "×"
                        "ALT_TAB_OPEN" -> "Apps"
                        "ALT_TAB_NEXT" -> "Next"
                        "ALT_TAB_CLOSE" -> "Choose"
                        else -> title
                    }
                    TextView(this).apply {
                        text = label
                        textSize = if (label.length > 4) 10f else if (label.length > 2) 13f else 25f
                        setTypeface(null, Typeface.BOLD)
                        setTextColor(white)
                        gravity = Gravity.CENTER
                        maxLines = 1
                        includeFontPadding = false
                        circle.addView(this, FrameLayout.LayoutParams(-1, -1))
                    }
                }
                circle.setOnClickListener {
                    sendAction(type, value)
                    if (value == "MEDIA_PLAY_PAUSE" && icon != null) {
                        showingPause = !showingPause
                        icon.setImageResource(if (showingPause) R.drawable.pb_media_pause else R.drawable.pb_media_play)
                        circle.contentDescription = if (showingPause) "Pause media" else "Play media"
                    }
                }
            }
        }
        controlRow(listOf(
            Triple("Volume down", "key", "VOLUME_DOWN"),
            Triple("Volume up", "key", "VOLUME_UP"),
            Triple("Mute", "key", "VOLUME_MUTE"),
            Triple("Previous track", "key", "MEDIA_PREV"),
            Triple("Play or pause media", "key", "MEDIA_PLAY_PAUSE"),
            Triple("Next track", "key", "MEDIA_NEXT")))
        controlRow(listOf(
            Triple("Apps", "shortcut", "ALT_TAB_OPEN"),
            Triple("Next app", "shortcut", "ALT_TAB_NEXT"),
            Triple("Choose", "shortcut", "ALT_TAB_CLOSE")))
        controlRow(listOf(
            Triple("Copy", "shortcut", "COPY"),
            Triple("Select all and copy", "shortcut", "SELECT_ALL_COPY"),
            Triple("Paste", "shortcut", "PASTE")))
        controlRow(listOf(
            Triple("Esc", "key", "ESCAPE"),
            Triple("Tab", "key", "TAB"),
            Triple("Enter", "key", "ENTER"),
            Triple("Backspace", "key", "BACKSPACE")))
        // Keep a landscape trackpad, never let it expand into portrait.
        // Use only residual vertical space after the header, editor, and ALL
        // action rows are laid out; extra room remains dark and empty.
        root.viewTreeObserver.addOnGlobalLayoutListener {
            val maxLandscape = ((root.width - root.paddingLeft - root.paddingRight) / 1.85f).toInt()
            val fixed = root.childrenHeightExcept(trackpad) + root.paddingTop + root.paddingBottom
            val available = (root.height - fixed - dp(5)).coerceAtLeast(dp(48))
            val target = minOf(maxLandscape, available, dp(135))
            if (trackpad.layoutParams.height != target) {
                trackpad.layoutParams = trackpad.layoutParams.apply { height = target }
            }
        }
        root.requestFocus()
        if (prefs.getString("host", null) != null) startConnection()
        else discover()
    }

    private fun LinearLayout.childrenHeightExcept(excluded: View): Int {
        var total = 0
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child === excluded || child.visibility == View.GONE) continue
            val params = child.layoutParams as? LinearLayout.LayoutParams
            total += child.measuredHeight + (params?.topMargin ?: 0) + (params?.bottomMargin ?: 0)
        }
        return total
    }

    private fun discover() {
        discoveryButton.isEnabled = false
        status.text = "Searching your Wi-Fi for PocketBoard..."
        Thread {
            val found = linkedMapOf<String, String>()
            val lock = (getSystemService(Context.WIFI_SERVICE) as WifiManager)
                .createMulticastLock("pocketkeyboard-discover")
            try {
                lock.setReferenceCounted(false)
                lock.acquire()
                DatagramSocket().use { socket ->
                    socket.broadcast = true
                    socket.soTimeout = 350
                    val payload = "POCKETKEYBOARD_DISCOVER_V1".toByteArray(Charsets.US_ASCII)
                    val destinations = mutableSetOf("255.255.255.255")
                    try {
                        for (iface in java.net.NetworkInterface.getNetworkInterfaces().toList()) {
                            for (address in iface.interfaceAddresses) {
                                address.broadcast?.hostAddress?.let { destinations.add(it) }
                            }
                        }
                    } catch (_: Exception) {}
                    destinations.forEach {
                        try {
                            socket.send(DatagramPacket(payload, payload.size, InetAddress.getByName(it), 38477))
                        } catch (_: Exception) {}
                    }
                    val deadline = System.currentTimeMillis() + 2200
                    while (System.currentTimeMillis() < deadline) {
                        val buffer = ByteArray(1200)
                        val packet = DatagramPacket(buffer, buffer.size)
                        try {
                            socket.receive(packet)
                            val response = JSONObject(String(packet.data, 0, packet.length, Charsets.UTF_8))
                            if (response.optString("type") == "pocketkeyboard_pc") {
                                val address = packet.address.hostAddress ?: continue
                                val name = response.optString("name", address)
                                found[address] = "$name ($address)"
                            }
                        } catch (_: SocketTimeoutException) {}
                          catch (_: Exception) {}
                    }
                }
            } catch (e: Exception) {
                runOnUiThread { status.text = "Discovery error: ${e.message}" }
            } finally {
                if (lock.isHeld) lock.release()
            }
            runOnUiThread {
                discoveryButton.isEnabled = true
                if (isFinishing || isDestroyed) return@runOnUiThread
                if (found.isEmpty()) {
                    status.text = "No PC found. Check same Wi-Fi and firewall."
                    return@runOnUiThread
                }
                val hosts = found.keys.toList()
                android.app.AlertDialog.Builder(this)
                    .setTitle("Connect to a PC")
                    .setItems(hosts.map { found[it] }.toTypedArray()) { _, index ->
                        host.setText(hosts[index])
                        startConnection()
                    }
                    .setNegativeButton("Cancel", null)
                    .show()
            }
        }.start()
    }

    private class RainbowPad(context: Context) : View(context) {
        private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
        private val colors = intArrayOf(
            0xFFE53935.toInt(), 0xFFFF8C23.toInt(), 0xFFFFDD33.toInt(),
            0xFF42B85A.toInt(), 0xFF2787E5.toInt(), 0xFF4849C4.toInt(),
            0xFF9C4BCB.toInt())
        override fun onDraw(canvas: Canvas) {
            super.onDraw(canvas)
            val w = width.toFloat()
            val h = height.toFloat()
            val r = resources.displayMetrics.density * 12
            val shape = Path().apply { addRoundRect(RectF(0f, 0f, w, h), r, r, Path.Direction.CW) }
            canvas.save()
            canvas.clipPath(shape)
            val span = w / 7f
            val lean = kotlin.math.min(h * 0.14f, span * 0.35f)
            // Antialiased seam safety: even subpixel rounding cannot show
            // the charcoal view background through the stripes.
            canvas.drawColor(colors[0])
            for (i in colors.indices) {
                paint.color = colors[i]
                val leftTop = if (i == 0) -w else i * span - lean
                val leftBottom = if (i == 0) -w else i * span + lean
                val rightTop = if (i == colors.lastIndex) 2f*w else (i+1) * span - lean + 1f
                val rightBottom = if (i == colors.lastIndex) 2f*w else (i+1) * span + lean + 1f
                val stripe = Path().apply {
                    moveTo(leftTop, 0f)
                    lineTo(rightTop, 0f)
                    lineTo(rightBottom, h)
                    lineTo(leftBottom, h)
                    close()
                }
                canvas.drawPath(stripe, paint)
            }
            canvas.restore()
            val d = resources.displayMetrics.density
            val cx = w * 0.5f
            val cy = h * 0.5f
            val pointer = Path().apply {
                moveTo(cx - 7*d, cy - 12*d)
                lineTo(cx - 7*d, cy + 10*d)
                lineTo(cx - 1*d, cy + 5*d)
                lineTo(cx + 5*d, cy + 15*d)
                lineTo(cx + 10*d, cy + 12*d)
                lineTo(cx + 4*d, cy + 2*d)
                lineTo(cx + 12*d, cy + 1*d)
                close()
            }
            paint.color = Color.WHITE
            paint.style = Paint.Style.STROKE
            paint.strokeWidth = 2.5f * d
            paint.strokeJoin = Paint.Join.ROUND
            canvas.drawPath(pointer, paint)
            paint.style = Paint.Style.FILL
            paint.color = 0xAA222A48.toInt()
            canvas.drawPath(pointer, paint)
            paint.style = Paint.Style.STROKE
            paint.color = Color.WHITE
            paint.strokeWidth = 1.2f * d
            canvas.drawRoundRect(RectF(d, d, w-d, h-d), 12*d, 12*d, paint)
            paint.style = Paint.Style.FILL
        }
    }

    private fun showStatus(message: String) = runOnUiThread {
        status.text = if (ready) "●  Connected securely to " + prefs.getString("host", "PC") else message
        status.setTextColor(if (ready) 0xFFE5FFEE.toInt() else 0xFFDDE8FF.toInt())
        status.background = bg(if (ready) 0xFF135D35.toInt() else 0xFF283040.toInt(), 14)
        editor.isEnabled = ready
        if (ready && !firstReady) {
            firstReady = true
            editor.requestFocus()
            editor.postDelayed({
                (getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager)
                    .showSoftInput(editor, InputMethodManager.SHOW_IMPLICIT)
            }, 220)
        }
    }

    private fun send(json: JSONObject) {
        if (!ready) return
        if (json.optString("type") == "local") {
            ignoreEdit = true
            editor.setText("")
            previous = ""
            ignoreEdit = false
            return
        }
        if (!outgoing.offer(json.toString())) showStatus("Input buffer full; reconnect.")
    }

    private fun startConnection() {
        val address = host.text.toString().trim()
        if (address.isEmpty()) { showStatus("Discover your PC first"); return }
        val previousHost = prefs.getString("host", null)
        if (previousHost != address) prefs.edit().remove("token").remove("pin").apply()
        prefs.edit().putString("host", address).apply()
        connectedSocket?.close()
        worker?.interrupt()
        outgoing.clear()
        firstReady = false
        worker = Thread { connectLoop(address) }.also { it.start() }
    }

    private fun connectLoop(address: String) {
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
                    output.write(JSONObject().put("type", "enroll").toString() + "\n")
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
