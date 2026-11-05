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
import android.text.style.ImageSpan
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
    private lateinit var discoveryButton: ImageView
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

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()
    private fun bg(color: Int, radius: Int = 12) = GradientDrawable().apply {
        setColor(color)
        cornerRadius = dp(radius).toFloat()
    }
    private fun sendAction(type: String, value: String) =
        send(JSONObject().put("type", type).put("value", value))

    // Tint the exact traced vector silhouette. Its matching mask clips ripples
    // to the same irregular contour without affecting the independent glyph.
    private fun circularButton(color: Int, shapeRes: Int): android.graphics.drawable.Drawable {
        val surface = getDrawable(shapeRes)!!.mutate().apply { setTint(color) }
        val mask = getDrawable(shapeRes)!!.mutate()
        return RippleDrawable(ColorStateList.valueOf(PocketBoardPalette.PRESS_RIPPLE), surface, mask)
    }
    private fun statusShape(color: Int): android.graphics.drawable.Drawable =
        getDrawable(R.drawable.pb_shape_connected)!!.mutate().apply { setTint(color) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setSoftInputMode(
            WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE or
                WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_VISIBLE
        )
        window.statusBarColor = PocketBoardPalette.CHARCOAL
        window.navigationBarColor = PocketBoardPalette.CHARCOAL
        val charcoal = PocketBoardPalette.CHARCOAL
        val cream = PocketBoardPalette.CREAM
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
            setImageResource(R.drawable.pb_header_icon)
            contentDescription = "PocketBoard rainbow keyboard logo"
            top.addView(this, LinearLayout.LayoutParams(dp(40), dp(40)).apply { rightMargin = dp(7) })
        }
        // Connection and discovery share the icon's header row.
        status = TextView(this).apply {
            text = "Disconnected"
            textSize = 13f
            typeface = resources.getFont(R.font.morning_rainbow)
            setTextColor(PocketBoardPalette.CREAM)
            gravity = Gravity.CENTER
            maxLines = 1
            ellipsize = android.text.TextUtils.TruncateAt.END
            background = statusShape(PocketBoardPalette.DISCONNECTED)
            top.addView(this, LinearLayout.LayoutParams(0, dp(40), 1f).apply { rightMargin = dp(7) })
        }
        discoveryButton = ImageView(this).apply {
            setImageResource(R.drawable.pb_discover)
            imageTintList = ColorStateList.valueOf(cream)
            setPadding(dp(11), dp(11), dp(11), dp(11))
            contentDescription = "Discover nearby PCs"
            background = circularButton(PocketBoardPalette.PURPLE, R.drawable.pb_shape_search)
            isClickable = true
            isFocusable = true
            setOnClickListener { discover() }
            top.addView(this, LinearLayout.LayoutParams(dp(40), dp(40)))
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
                touchpadFeedback.text = ""
                return true
            }
            override fun onDoubleTap(e: MotionEvent): Boolean {
                sendAction("mouse_click", "double")
                touchpadFeedback.text = ""
                return true
            }
            override fun onLongPress(e: MotionEvent) {
                sendAction("mouse_click", "right")
                touchpadFeedback.text = ""
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
                    touchpadFeedback.text = ""
                }
                return true
            }
        })
        val trackpad = RainbowPad(this).apply {
            contentDescription = "Rainbow touchpad. Slide to move pointer, tap to click, hold to right-click"
            setOnTouchListener { _, event -> detector.onTouchEvent(event); true }
        }
        val trackpadParams = LinearLayout.LayoutParams(-1, dp(146)).apply {
            // Match the 2dp pad margin + 16dp feedback area below it.
            topMargin = dp(18)
            bottomMargin = dp(2)
        }
        root.addView(trackpad, trackpadParams)
        touchpadFeedback = TextView(this).apply {
            text = ""
            setTextColor(PocketBoardPalette.MUTED_CREAM)
            textSize = 11f
            root.addView(this, LinearLayout.LayoutParams(-1, dp(16)))
        }
        val inputBar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            background = bg(PocketBoardPalette.DISCONNECTED, 13)
            root.addView(this, LinearLayout.LayoutParams(-1, dp(41)).apply { bottomMargin = dp(15) })
        }
        editor = EditText(this).apply {
            hint = "Type or dictate on the PC"
            setHintTextColor(PocketBoardPalette.HINT_CREAM)
            setTextColor(cream)
            typeface = resources.getFont(R.font.morning_rainbow)
            textSize = 16f
            setSingleLine(false)
            maxLines = 2
            inputType = android.text.InputType.TYPE_CLASS_TEXT or
                android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE or
                android.text.InputType.TYPE_TEXT_FLAG_AUTO_CORRECT or
                android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
            background = null
            setPadding(dp(12), dp(2), 0, dp(2))
            // The IME owns keyboard focus even while discovering/reconnecting.
            // Sending stays gated by ready in send(); local editing remains available.
            isEnabled = true
            isFocusableInTouchMode = true
            inputBar.addView(this, LinearLayout.LayoutParams(0, dp(41), 1f))
        }
        // The input field owns Clear and Dictation.
        fun inputAction(name: String, iconRes: Int, color: Int, shapeRes: Int, action: () -> Unit) {
            val holder = FrameLayout(this).apply {
                isClickable = true
                isFocusable = true
                contentDescription = name
                setOnClickListener { action() }
                inputBar.addView(this, LinearLayout.LayoutParams(dp(40), dp(41)))
            }
            ImageView(this).apply {
                setImageResource(iconRes)
                imageTintList = ColorStateList.valueOf(cream)
                setPadding(dp(6), dp(6), dp(6), dp(6))
                background = circularButton(color, shapeRes)
                isClickable = false
                holder.addView(this, FrameLayout.LayoutParams(dp(34), dp(34), Gravity.CENTER))
            }
        }
        inputAction("Clear text input", R.drawable.pb_clear, PocketBoardPalette.RED_PINK, R.drawable.pb_shape_clear) {
            sendAction("local", "CLEAR")
        }
        inputAction("Open keyboard for voice dictation", R.drawable.pb_mic, PocketBoardPalette.PURPLE, R.drawable.pb_shape_microphone) {
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
        val palettes = PocketBoardPalette.BUTTON_COLORS
        var buttonIndex = 0
        var showingPause = false // presentation-only: no media state queries
        fun resourceFor(value: String): Int? = when (value) {
            "VOLUME_DOWN" -> R.drawable.pb_volume_down
            "VOLUME_UP" -> R.drawable.pb_volume_up
            "VOLUME_MUTE" -> R.drawable.pb_volume_mute
            "MEDIA_PREV" -> R.drawable.pb_media_prev
            "MEDIA_NEXT" -> R.drawable.pb_media_next
            "MEDIA_PLAY_PAUSE" -> R.drawable.pb_media_play
            "COPY" -> R.drawable.pb_copy
            "SELECT_ALL_COPY" -> R.drawable.pb_all_copy
            "PASTE" -> R.drawable.pb_paste
            "ALT_TAB_CLOSE" -> R.drawable.pb_connected_check
            "ALT_TAB_OPEN" -> R.drawable.pb_apps
            "TAB" -> R.drawable.pb_tab
            "ENTER" -> R.drawable.pb_enter
            "ESCAPE" -> R.drawable.pb_escape
            else -> null
        }
        // Shape and symbol identities are independent; play/pause shares one
        // traced silhouette and changes only its foreground symbol.
        fun shapeFor(value: String): Int = when (value) {
            "VOLUME_DOWN" -> R.drawable.pb_shape_volume_down
            "VOLUME_UP" -> R.drawable.pb_shape_volume_up
            "VOLUME_MUTE" -> R.drawable.pb_shape_mute
            "MEDIA_PREV" -> R.drawable.pb_shape_previous_track
            "MEDIA_NEXT" -> R.drawable.pb_shape_next_track
            "MEDIA_PLAY_PAUSE" -> R.drawable.pb_shape_pause
            "ALT_TAB_OPEN", "ALT_TAB_CLOSE" -> R.drawable.pb_shape_apps_grid
            "COPY" -> R.drawable.pb_shape_overlapping_windows
            "SELECT_ALL_COPY" -> R.drawable.pb_shape_windows_check
            "PASTE" -> R.drawable.pb_shape_windows_plus
            "ESCAPE" -> R.drawable.pb_shape_escape
            "TAB" -> R.drawable.pb_shape_tab
            "ENTER" -> R.drawable.pb_shape_enter
            else -> error("Unmapped silhouette: $value")
        }
        fun controlRow(actions: List<Triple<String, String, String>>, buttonSize: Int = 49) {
            val row = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
                root.addView(this, LinearLayout.LayoutParams(-1, dp(53)).apply { topMargin = dp(3) })
            }
            actions.forEach { (title, type, value) ->
                val slot = FrameLayout(this).apply {
                    row.addView(this, LinearLayout.LayoutParams(0, dp(53), 1f))
                }
                if (value == "EMPTY") return@forEach
                val color = palettes[(buttonIndex++) % palettes.size]
                val circle = FrameLayout(this).apply {
                    background = circularButton(color, shapeFor(value))
                    contentDescription = title
                    isFocusable = true
                    isClickable = true
                    slot.addView(this, FrameLayout.LayoutParams(dp(buttonSize), dp(buttonSize), Gravity.CENTER))
                }
                val symbol = resourceFor(value)
                val icon: ImageView? = if (symbol != null) ImageView(this).apply {
                    setImageResource(symbol)
                    imageTintList = ColorStateList.valueOf(cream)
                    setPadding(dp(8), dp(8), dp(8), dp(8))
                    circle.addView(this, FrameLayout.LayoutParams(dp(buttonSize), dp(buttonSize), Gravity.CENTER))
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
                        typeface = resources.getFont(R.font.morning_rainbow)
                        setTextColor(cream)
                        gravity = Gravity.CENTER
                        maxLines = 1
                        includeFontPadding = false
                        circle.addView(this, FrameLayout.LayoutParams(dp(buttonSize), dp(buttonSize), Gravity.CENTER))
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
            Triple("Next track", "key", "MEDIA_NEXT")), buttonSize = 45)
        // App switching and clipboard form one compact six-button row.
        // Keep the related Apps -> Next -> Choose sequence adjacent.
        controlRow(listOf(
            Triple("Apps", "shortcut", "ALT_TAB_OPEN"),
            Triple("Choose", "shortcut", "ALT_TAB_CLOSE"),
            Triple("", "", "EMPTY"),
            Triple("Copy", "shortcut", "COPY"),
            Triple("Select all and copy", "shortcut", "SELECT_ALL_COPY"),
            Triple("Paste", "shortcut", "PASTE")))
        controlRow(listOf(
            Triple("", "", "EMPTY"),
            Triple("", "", "EMPTY"),
            Triple("", "", "EMPTY"),
            Triple("Esc", "key", "ESCAPE"),
            Triple("Tab", "key", "TAB"),
            Triple("Enter", "key", "ENTER")), buttonSize = 51)
        // Keep a landscape trackpad, never let it expand into portrait.
        // Use only residual vertical space after the header, editor, and ALL
        // action rows are laid out; extra room remains dark and empty.
        root.viewTreeObserver.addOnGlobalLayoutListener {
            val maxLandscape = ((root.width - root.paddingLeft - root.paddingRight) / 1.85f).toInt()
            val fixed = root.childrenHeightExcept(trackpad) + root.paddingTop + root.paddingBottom
            // Reserve both pad margins when the IME leaves very little vertical space.
            val padMargins = trackpadParams.topMargin + trackpadParams.bottomMargin
            val available = (root.height - fixed - padMargins).coerceAtLeast(dp(48))
            val target = minOf(maxLandscape, available, dp(158))
            if (trackpad.layoutParams.height != target) {
                trackpad.layoutParams = trackpad.layoutParams.apply { height = target }
            }
        }
        // Focus the text sink before any pairing/network activity. All keyboard
        // input goes here without requiring the user to tap the field first.
        editor.requestFocus()
        if (prefs.getString("host", null) != null) startConnection()
        else discover()
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (!hasFocus || !::editor.isInitialized || isFinishing || isDestroyed) return
        editor.post {
            // Do not steal focus from a dialog, another app, or TalkBack while
            // PocketBoard isn't foregrounded. Android controls the actual IME.
            if (!window.decorView.hasWindowFocus() || isFinishing || isDestroyed) return@post
            editor.requestFocus()
            (getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager)
                .showSoftInput(editor, InputMethodManager.SHOW_IMPLICIT)
        }
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
        status.text = "Searching..."
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
                runOnUiThread { status.text = "Discovery error" }
            } finally {
                if (lock.isHeld) lock.release()
            }
            runOnUiThread {
                discoveryButton.isEnabled = true
                if (isFinishing || isDestroyed) return@runOnUiThread
                if (found.isEmpty()) {
                    status.text = "No PC found"
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
            PocketBoardPalette.RED_PINK, PocketBoardPalette.ORANGE,
            PocketBoardPalette.YELLOW, PocketBoardPalette.GREEN,
            PocketBoardPalette.TEAL, PocketBoardPalette.BLUE,
            PocketBoardPalette.PURPLE)
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
            paint.color = PocketBoardPalette.CREAM
            paint.style = Paint.Style.STROKE
            paint.strokeWidth = 2.5f * d
            paint.strokeJoin = Paint.Join.ROUND
            canvas.drawPath(pointer, paint)
            paint.style = Paint.Style.FILL
            paint.color = PocketBoardPalette.DISCONNECTED
            canvas.drawPath(pointer, paint)
            paint.style = Paint.Style.STROKE
            paint.color = PocketBoardPalette.CREAM
            paint.strokeWidth = 1.2f * d
            canvas.drawRoundRect(RectF(d, d, w-d, h-d), 12*d, 12*d, paint)
            paint.style = Paint.Style.FILL
        }
    }

    private fun showStatus(message: String) = runOnUiThread {
        val label = if (ready) "Connected" else when {
            message.startsWith("Disconnected") -> "Disconnected"
            message.startsWith("Connecting") -> "Connecting..."
            else -> message
        }
        if (ready) {
            // Inline image span means TextView centers the whole label + checkmark,
            // rather than placing the checkmark against the status panel's right edge.
            val combined = SpannableString("$label  \uFFFC")
            getDrawable(R.drawable.pb_connected_check)?.mutate()?.let { check ->
                check.setTint(PocketBoardPalette.CREAM)
                check.setBounds(0, 0, dp(19), dp(19))
                combined.setSpan(
                    ImageSpan(check, ImageSpan.ALIGN_CENTER),
                    combined.length - 1, combined.length,
                    android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE
                )
            }
            status.text = combined
        } else {
            status.text = label
        }
        status.contentDescription = label
        status.setTextColor(PocketBoardPalette.CREAM)
        status.background = statusShape(if (ready) PocketBoardPalette.GREEN else PocketBoardPalette.DISCONNECTED)
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
