package dev.gbidevelopment.fontshelf;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.ValueCallback;
import androidx.activity.ComponentActivity;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.webkit.WebViewAssetLoader;

/** Minimal trusted-origin shell. No broad storage permissions or JS-to-Java bridge. */
public final class MainActivity extends ComponentActivity {
    private static final String HOME = "https://appassets.androidplatform.net/assets/index.html";
    private static final String ORIGIN = "https://appassets.androidplatform.net";
    private WebView webView;
    private ValueCallback<Uri[]> fileCallback;

    private final ActivityResultLauncher<Intent> picker =
        registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result -> {
            ValueCallback<Uri[]> callback = fileCallback;
            fileCallback = null;
            if (callback == null) return;
            if (result.getResultCode() != Activity.RESULT_OK) {
                callback.onReceiveValue(null);
                return;
            }
            Intent data = result.getData();
            if (data == null) {
                callback.onReceiveValue(null);
                return;
            }
            if (data.getClipData() != null) {
                int count = data.getClipData().getItemCount();
                Uri[] uris = new Uri[count];
                for (int i = 0; i < count; i++) uris[i] = data.getClipData().getItemAt(i).getUri();
                callback.onReceiveValue(uris);
            } else if (data.getData() != null) {
                callback.onReceiveValue(new Uri[]{data.getData()});
            } else {
                callback.onReceiveValue(null);
            }
        });

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
            .build();
        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(true); // Read only documents chosen in Android's system picker.
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        webView.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if (ORIGIN.equals(url.getScheme() + "://" + url.getAuthority())) return false;
                if (url.getScheme().equals("https")) {
                    Intent external = new Intent(Intent.ACTION_VIEW, url);
                    try { startActivity(external); } catch (ActivityNotFoundException ignored) {}
                }
                return true;
            }
        });
        webView.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback,
                FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.setType("*/*");
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, params.getMode() == FileChooserParams.MODE_OPEN_MULTIPLE);
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                try { picker.launch(intent); return true; }
                catch (ActivityNotFoundException error) {
                    fileCallback = null;
                    callback.onReceiveValue(null);
                    return false;
                }
            }
        });
        setContentView(webView);
        webView.loadUrl(HOME);
    }

    @Override public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override protected void onDestroy() {
        if (fileCallback != null) {
            fileCallback.onReceiveValue(null);
            fileCallback = null;
        }
        if (webView != null) {
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
