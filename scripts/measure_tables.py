import sys
from playwright.sync_api import sync_playwright
url=sys.argv[1]; W=int(sys.argv[2]) if len(sys.argv)>2 else 1280
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':W,'height':900}); pg.goto(url,wait_until='domcontentloaded'); pg.wait_for_timeout(1500)
    r=pg.evaluate("""()=>[...document.querySelectorAll('#wiki-body .markdown-body table')].map((t,i)=>{let h=t.previousElementSibling;while(h&&!/^H[1-4]$/.test(h.tagName))h=h.previousElementSibling;return [i,t.querySelectorAll('tr').length,t.querySelector('tr').children.length,t.scrollWidth,t.clientWidth,(h?h.textContent.trim():'').slice(0,45)]})""")
    for x in r: print(('SCROLLS' if x[3]>x[4]+1 else 'fits   '),x)
    b.close()
