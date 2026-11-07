package dev.gbidevelopment.fontshelf;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import android.os.SystemClock;
import android.view.ViewGroup;
import android.webkit.WebView;
import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.Test;
import org.junit.runner.RunWith;

/**
 * Installed-product acceptance: real WebView, app-assets origin, IndexedDB,
 * FontFace loading and lifecycle restoration. Uses a bundled TTF rather than
 * a mocked font. External document-provider intake remains a separate gate.
 */
@RunWith(AndroidJUnit4.class)
public final class InstalledLibraryTest {
    private WebView webView;

    private void attach(ActivityScenario<MainActivity> scenario) {
        scenario.onActivity(activity -> {
            ViewGroup root = activity.findViewById(android.R.id.content);
            webView = (WebView) root.getChildAt(0);
        });
    }

    private String eval(String source) throws Exception {
        CountDownLatch done = new CountDownLatch(1);
        AtomicReference<String> value = new AtomicReference<>();
        InstrumentationRegistry.getInstrumentation().runOnMainSync(
            () -> webView.evaluateJavascript(source, result -> {
                value.set(result);
                done.countDown();
            })
        );
        assertTrue("WebView JavaScript callback did not complete",done.await(15,TimeUnit.SECONDS));
        return value.get();
    }

    private void waitFor(String expression) throws Exception {
        long until = SystemClock.uptimeMillis() + 45000;
        String last = "";
        while (SystemClock.uptimeMillis() < until) {
            last = eval(expression);
            if ("true".equals(last)) return;
            Thread.sleep(220);
        }
        fail("Timed out checking "+expression+"; last result: "+last+
             ", smoke status: "+eval("window.__fontShelfSmoke || null"));
    }

    private void waitReady() throws Exception {
        waitFor("document.readyState === 'complete' && typeof loading !== 'undefined' && !loading && libraryReady");
    }

    @Test public void savedFontSurvivesDismissalActivityRestartAndNamedLists() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            attach(scenario);
            waitReady();
            assertEquals("true",eval("document.querySelector('h1').textContent.includes('SHELF')"));
            assertEquals("true",eval("typeof window.fflate.unzipSync === 'function'"));

            eval("""
                window.__fontShelfSmoke = 'working';
                void (async function() {
                  const response=await fetch('./P22%20Stanyan%20Regular%20Regular.ttf');
                  if(!response.ok)throw Error('bundled TTF request failed');
                  const bytes=new Uint8Array(await response.arrayBuffer());
                  if(bytes.length<1000)throw Error('empty bundled TTF');
                  const kit=await getFontkit();
                  const parsed=kit.create(bytes);
                  if(!parsed?.characterSet?.length)throw Error('offline font parser failed');
                  const zipped=window.fflate.zipSync({'specimen.ttf':bytes});
                  const unzipped=window.fflate.unzipSync(zipped)['specimen.ttf'];
                  if(unzipped.length!==bytes.length)throw Error('offline ZIP roundtrip failed');
                  const meta={
                    id:'fs9000',key:'android-installed-smoke-v1',
                    variant:'android-installed-smoke-v1',
                    name:'P22 Stanyan Fixture',familyName:'P22 Stanyan Fixture',
                    familyKey:'p22stanyanfixture',styleName:'Regular',
                    file:'P22 Stanyan Regular Regular.ttf',
                    source:'P22 Stanyan Regular Regular.ttf',
                    cps:[65,66,67],axes:[],hidden:false,tags:[],familyTags:[]
                  };
                  await FontLibrary.save(meta,bytes);
                  catalog.set(meta.id,meta);
                  counter=Math.max(counter,9000);
                  await revive(meta);
                  render();
                  if(cardsByFamily.size!==1)throw Error('font card missing after restore');
                  window.__fontShelfSmoke='saved';
                })().catch(e=>{window.__fontShelfSmoke='ERROR '+e.message});
                """);
            waitFor("window.__fontShelfSmoke === 'saved'");

            eval("""
                window.__fontShelfSmoke='working';
                void (async function() {
                  const family=[...groupsNow().keys()][0];
                  await removeFamily(family);
                  const meta=await FontLibrary.get('fonts','fs9000');
                  const bytes=await FontLibrary.get('data','fs9000');
                  if(!meta.hidden||!bytes?.bytes)throw Error('dismissal removed saved font bytes');
                  if(cardsByFamily.size!==0)throw Error('dismissal left a visible card');
                  window.__fontShelfSmoke='hidden';
                })().catch(e=>{window.__fontShelfSmoke='ERROR '+e.message});
                """);
            waitFor("window.__fontShelfSmoke === 'hidden'");

            scenario.recreate();
            attach(scenario);
            waitReady();
            assertEquals("true",eval("catalog.has('fs9000') && catalog.get('fs9000').hidden && !records.has('fs9000')"));

            eval("""
                window.__fontShelfSmoke='working';
                void (async function() {
                  await toggleLibraryGroup([catalog.get('fs9000')],true);
                  if(!records.has('fs9000'))throw Error('library restore failed');
                  if(cardsByFamily.size!==1)throw Error('restored card absent');
                  const meta=catalog.get('fs9000');
                  meta.tags=['specimen'];
                  meta.familyTags=['handwriting'];
                  await FontLibrary.update(meta);
                  const list={id:'installed-smoke',title:'Saved specimens',ids:['fs9000']};
                  await FontLibrary.saveList(list);
                  savedLists.set(list.id,list);
                  window.__fontShelfSmoke='organized';
                })().catch(e=>{window.__fontShelfSmoke='ERROR '+e.message});
                """);
            waitFor("window.__fontShelfSmoke === 'organized'");

            scenario.recreate();
            attach(scenario);
            waitReady();
            assertEquals("true",eval("""
                records.has('fs9000') &&
                cardsByFamily.size===1 &&
                catalog.get('fs9000')?.tags?.includes('specimen') &&
                catalog.get('fs9000')?.familyTags?.includes('handwriting') &&
                savedLists.get('installed-smoke')?.ids?.includes('fs9000')
                """));
        }
    }
}
