import os
import django
import sys
import time

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gwz.settings')
django.setup()

from store.models import SiteSettings, Category, Page

def update_content():
    print("Updating GWZ content to Traditional Chinese...")
    
    # 1. Update SiteSettings
    # Use default=1 or similar if needed, assuming there's only one settings object
    site_settings, _ = SiteSettings.objects.get_or_create(id=1)
    site_settings.site_name = "GWZ"
    site_settings.hero_title = "平凡中見不凡"
    site_settings.hero_subtitle = "跟著王子的味覺去生活"
    site_settings.founder_name = "王子"
    site_settings.founder_intro_title = "平凡中見不凡"
    site_settings.founder_intro_text = "加入王子的美食之旅，享受生活中的美好事物！"
    site_settings.feature_title = "GWZ Live・In Style"
    site_settings.feature_subtitle = "Discover the art of living well."
    
    # Menu Text
    site_settings.menu_home_text = "首頁"
    site_settings.menu_about_text = "關於GWZ"
    site_settings.menu_videos_text = "王子煮場"
    site_settings.menu_lifestyle_text = "味覺足跡"
    site_settings.menu_store_text = "GWZ商店"
    site_settings.menu_contact_text = "聯絡我們"
    
    site_settings.save()
    print("SiteSettings updated.")

    # 1. Update Categories (Translate to Chinese)
    # The user said "Directory is corresponding to product categories"
    # We will rename existing categories to Chinese
    category_map = {
        "featured": "精選",
        "blog": "博客",
        "recipes": "食譜",
        "food-review": "食評",
        "lifestyle": "生活風格",
        "products": "產品",
    }
    
    for slug, name in category_map.items():
        cat, created = Category.objects.get_or_create(slug=slug)
        cat.name = name
        cat.save()
        print(f"Category updated: {slug} -> {name}")

    # 2. Create About Us Page
    # User asked for "About Us" (關於我們)
    about_page, created = Page.objects.get_or_create(slug='about-us')
    about_page.title = "關於GWZ"
    about_page.content = """
    <p class="lead mt-4">GWZ 是由王子於 2017 年創立的品牌，致力於推廣烹飪文化和享受品質生活。</p>
    
    <p>王子熱愛汽車、時尚與音樂，但最鍾情的始終是美食。這份熱情源於英國留學期間，面對昂貴的外食與難覓的道地中菜，他因思念家鄉風味而走進市場與廚房。從探索食材開始，他重尋記憶中的味道，也展開了屬於他的料理旅程。</p>

    <p>他相信烹飪是一門藝術，更是與所愛之人交流分享的橋樑。食物不僅是日常所需，更能跨越語言，促進不同文化間的溝通與連結，拉近人與人之間的距離。</p>

    <h3 class="mt-5 fw-bold" style="color: var(--primary-purple);">里程碑</h3>
    <ul class="list-unstyled">
      <li class="mb-2"><i class="fas fa-check-circle me-2 text-success"></i> <strong>2018 年</strong>：開始製作烹飪影片，陸續於 YouTube（#王子煮場）與《明報》刊載，觸達超過 50 萬日讀者。</li>
      <li class="mb-2"><i class="fas fa-check-circle me-2 text-success"></i> <strong>2019–2020 年</strong>：主持烹飪節目「30 分鐘大放餸」，於香港開電視第 77 台播出。</li>
      <li class="mb-2"><i class="fas fa-check-circle me-2 text-success"></i> <strong>2020 年</strong>：開展內地平台（騰訊、抖音）內容：#乔治王子的品质生活。</li>
    </ul>

    <h3 class="mt-5 fw-bold" style="color: var(--primary-purple);">理念</h3>
    <p><strong>GWZ Live・In Style</strong></p>
    <p>我們持續在東西交會的香港汲取靈感，將味道、文化與生活方式相互串連。我們希望讓每一次料理都更有溫度與故事，讓每一位熱愛生活的人，都能在平凡日子裡創造不凡的味覺記憶。</p>

    <h3 class="mt-5 fw-bold" style="color: var(--primary-purple);">王子的88道拿手菜</h3>
    <div class="row align-items-center mt-4">
        <div class="col-md-4 mb-3 mb-md-0">
            <img src="/static/img/88_dishes_of_George.jpg" alt="王子的88道拿手菜" class="img-fluid rounded shadow-sm border">
        </div>
        <div class="col-md-8">
            <p>經過多年努力和準備，王子終於在 2021 年七月書展，推出了第一本個人菜譜——《王子的88道拿手菜》。在這本特別的食譜中，王子將他多年的烹調秘訣跟讀者分享，收錄了 88 道精選菜式，涵蓋多國料理。</p>
            <p>這本書亦是為了答謝多年支持和啟發他的祖父，是他令王子學懂欣賞有質素的食物和烹調技巧。這本書不僅是食譜，更是王子以食會友、分享人生之味的邀請。</p>
        </div>
    </div>
    
    <div class="row g-4 mt-2">
        <div class="col-md-6">
            <a href="/static/img/88_meat013.jpg" data-bs-toggle="modal" data-bs-target="#imageModal" data-bs-img="/static/img/88_meat013.jpg">
                <div class="ratio ratio-16x9">
                    <img src="/static/img/88_meat013.jpg" class="w-100 h-100 rounded shadow-sm" style="object-fit: cover; cursor: pointer;" alt="王子的88道拿手菜 - 肉類">
                </div>
            </a>
        </div>
        <div class="col-md-6">
            <a href="/static/img/88_seafood010.jpg" data-bs-toggle="modal" data-bs-target="#imageModal" data-bs-img="/static/img/88_seafood010.jpg">
                <div class="ratio ratio-16x9">
                    <img src="/static/img/88_seafood010.jpg" class="w-100 h-100 rounded shadow-sm" style="object-fit: cover; cursor: pointer;" alt="王子的88道拿手菜 - 海鮮">
                </div>
            </a>
        </div>
        <div class="col-md-6">
            <a href="/static/img/88_rice010.jpg" data-bs-toggle="modal" data-bs-target="#imageModal" data-bs-img="/static/img/88_rice010.jpg">
                <div class="ratio ratio-16x9">
                    <img src="/static/img/88_rice010.jpg" class="w-100 h-100 rounded shadow-sm" style="object-fit: cover; cursor: pointer;" alt="王子的88道拿手菜 - 飯類">
                </div>
            </a>
        </div>
        <div class="col-md-6">
            <a href="/static/img/88_rice013.jpg" data-bs-toggle="modal" data-bs-target="#imageModal" data-bs-img="/static/img/88_rice013.jpg">
                <div class="ratio ratio-16x9">
                    <img src="/static/img/88_rice013.jpg" class="w-100 h-100 rounded shadow-sm" style="object-fit: cover; cursor: pointer;" alt="王子的88道拿手菜 - 飯類">
                </div>
            </a>
        </div>
    </div>
    
    <div class="mt-5 p-4 bg-light rounded text-center border-start border-4 border-purple">
        <p class="lead mb-2 fst-italic">"Start learning new cooking skills today, with the best possible help."</p>
        <p class="mb-0 fw-bold text-secondary">—— 在我們的鼎力相助下，從今天開始學習烹飪技巧吧！</p>
    </div>
    """ # v1.8
    about_page.is_active = True
    about_page.save()
    print("Page 'About Us' created/updated.")
    
    # 3. Create core content pages for feature cards
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gallery_dir = os.path.join(project_root, 'media', 'gallery')
    gallery_files = []
    if os.path.isdir(gallery_dir):
        for fname in sorted(os.listdir(gallery_dir)):
            lower = fname.lower()
            if lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                gallery_files.append(fname)
    press_dir = os.path.join(project_root, 'media', 'press')
    press_files = []
    if os.path.isdir(press_dir):
        for fname in sorted(os.listdir(press_dir)):
            lower = fname.lower()
            if lower.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                press_files.append(fname)

    def build_gallery_block(files, category="gallery"):
        if not files:
            return ""
            
        # User requested: "Small images should be smaller", "Uniform layout", "Not messy"
        # We will use a strict grid of small square thumbnails.
        # Naming Convention: 
        # - *-hero.jpg: Main section image (handled manually in HTML)
        # - *-[number].jpg: Gallery thumbnails (handled here)
        
        items = []
        v = int(time.time())
        for f in files:
            items.append(f"""
            <div class="col-4 col-md-3 col-lg-2">
              <a href="#" class="d-block shadow-sm gallery-item" 
                 data-bs-toggle="modal" 
                 data-bs-target="#galleryModal" 
                 data-bs-image="/media/gallery/{f}?v={v}"
                 data-bs-category="{category}">
                <div class="ratio ratio-1x1">
                  <img src="/media/gallery/{f}?v={v}" alt="{os.path.splitext(f)[0]}" class="w-100 h-100" style="object-fit: cover;" loading="lazy">
                </div>
              </a>
            </div>
            """)
            
        return f"""
        <div class="row g-2 mt-4">
          {''.join(items)}
        </div>
        """
    g1 = gallery_files[0:4]
    g2 = gallery_files[4:8]
    g3 = gallery_files[8:12]
    # ---------------------------------------------------------
    # Naming Convention (Updated)
    # ---------------------------------------------------------
    # 1. Hero Images (Large Section Backgrounds/Images):
    #    - Format: [category]-hero.jpg
    #    - Examples: travel-hero.jpg, market-hero.jpg, kitchen-hero.jpg
    #    - Note: These are hardcoded in the HTML sections below.
    #
    # 2. Gallery Images (Small Square Thumbnails):
#    - Format: [category]-[number].jpg
#    - Examples: travel-01.jpg, travel-02.jpg, market-01.jpg
#    - Note: These are automatically picked up by the script and 
#            displayed as a grid of small square thumbnails.
#
# 3. Recommended Sizes:
#    - Hero Images:
#      * lifestyle-hero.jpg: 1920x1280 (65vh crop)
#      * travel-hero.jpg:    1200x900 (4:3)
#      * market-hero.jpg:    900x900 (1:1)
#      * kitchen-hero.jpg:   1920x864 (21:9)
#      * music-hero.jpg:     900x900 (1:1)
#      * moments-hero.jpg:   1920x1080 (16:9)
#
#    - Gallery Images:
#      * All gallery thumbnails: 1000x1000 pixels (Square crop recommended)
#        (This ensures high quality when opened in the lightbox, 
#         while CSS handles the small grid display)
#
# 4. File Extension:
#    - STRICTLY use .jpg (lowercase preferred, but code handles .JPG).
    # ---------------------------------------------------------

    def pick_set_for(prefix: str):
        print(f"Scanning for prefix: '{prefix}'...")
        numbered = []
        for f in gallery_files:
            lf = f.lower()
            if lf.startswith(prefix):
                base = os.path.splitext(lf)[0]
                # Skip hero images
                if base.endswith('-hero'):
                    print(f"  Skipping hero image: {f}")
                    continue
                
                # Check for numbered suffix (e.g. "01", "2")
                # We want to handle cases where there might be extra chars? 
                # User said "都是01. 02....", so strict digit check is good.
                tail = base[len(prefix):]
                if tail.isdigit():
                    numbered.append((int(tail), f))
                    print(f"  Found image: {f} (Index: {int(tail)})")
                else:
                    print(f"  Skipping non-numbered image: {f} (Tail: '{tail}')")
        
        # Sort by number (1, 2, 3...)
        numbered.sort(key=lambda x: x[0])
        
        # Return all found images (no limit)
        result = [f for _, f in numbered]
        print(f"Total for '{prefix}': {len(result)} images.\n")
        return result

    travel_set = pick_set_for('travel-')
    market_set = pick_set_for('market-')
    kitchen_set = pick_set_for('kitchen-')
    music_set = pick_set_for('music-')
    moments_set = pick_set_for('moments-')
    def build_press_block(files):
        if not files:
            return """
            <div class="text-muted">尚未加入媒體圖片。請將圖片上傳至 media/press 後再更新。</div>
            """
        items = []
        for f in files:
            base = os.path.splitext(f)[0]
            parts = base.split('_', 2)
            caption = base
            if len(parts) >= 2:
                media = parts[0]
                date_str = parts[1]
                caption = f"{media} {date_str}"
            items.append(f"""
            <div class="col-6 col-md-4 col-lg-3">
              <a href="/media/press/{f}" target="_blank" rel="noopener" class="d-block">
                <img src="/media/press/{f}" alt="{base}" class="img-fluid rounded border">
              </a>
              <div class="small text-muted mt-1">{caption}</div>
            </div>
            """)
        return f"""
        <div class="row g-3 mt-3">
          {''.join(items)}
        </div>
        """
    pages_data = [
        {
            'slug': 'featured',
            'title': '精選博客',
            'content': """
            <p>從王子的食譜與烹飪影片中獲得靈感，發現他對食材、火候與風味的獨到見解。</p>
            <p>我們挑選最值得一看的內容：料理思路、節慶靈感、廚房好物，讓家常菜也能有亮點。</p>

            <div class="mt-4">
              <h3 class="fw-bold">王子美食頻道</h3>
              <p class="text-muted">想看影片？先逛逛精選單集，或前往完整頻道頁。</p>
              <div class="row g-4">
                <div class="col-md-6">
                  <a href="https://youtu.be/3abQg-Er-Kk" target="_blank" rel="noopener" class="text-decoration-none">
                    <div class="card h-100 shadow-sm">
                      <img src="https://img.youtube.com/vi/3abQg-Er-Kk/hqdefault.jpg" alt="濟州黑毛豬的美味之旅" class="card-img-top">
                      <div class="card-body">
                        <h5 class="card-title fw-bold">濟州黑毛豬的美味之旅</h5>
                        <p class="card-text text-muted">探索濟州黑毛豬的在地風味與料理文化。</p>
                        <span class="btn btn-outline-primary btn-sm">在 YouTube 開啟</span>
                      </div>
                    </div>
                  </a>
                </div>
                <div class="col-md-6">
                  <a href="https://youtu.be/C47gUCemqzY" target="_blank" rel="noopener" class="text-decoration-none">
                    <div class="card h-100 shadow-sm">
                      <img src="https://img.youtube.com/vi/C47gUCemqzY/hqdefault.jpg" alt="五花腩煎炆芝麻斑食譜" class="card-img-top">
                      <div class="card-body">
                        <h5 class="card-title fw-bold">五花腩煎炆芝麻斑食譜</h5>
                        <p class="card-text text-muted">掌握火候與調味的關鍵，做出家常風味料理。</p>
                        <span class="btn btn-outline-primary btn-sm">在 YouTube 開啟</span>
                      </div>
                    </div>
                  </a>
                </div>
              </div>
              <div class="mt-3">
                <a href="/pages/waw-expert/" class="btn btn-dark rounded-pill px-4">前往頻道頁</a>
              </div>
            </div>
            """,
        },
        {
            'slug': 'blog',
            'title': '食譜與故事',
            'content': """
            <p class="text-muted text-center mb-5 lead">精選王子在烹飪、美食與旅遊上的精彩影片。</p><!-- v1.4 -->

            <h3 class="mt-4">播放清單</h3>
            <a href="https://youtube.com/playlist?list=PLEjO4hD4At7yhmox4RhnjRWaUujB24TZ2&si=DKOOyApX2E1pR2g8" target="_blank" class="text-decoration-none d-block">
                <div class="position-relative mb-4 shadow-lg border border-4 border-white rounded overflow-hidden">
                    <div class="ratio ratio-16x9">
                        <img src="/static/img/WAW_channel.png" class="w-100 h-100" style="object-fit: cover;" alt="WAW Expert - 王子">
                    </div>
                    <div class="position-absolute top-50 start-50 translate-middle" style="z-index: 10;">
                        <div style="width: 56px; height: 56px; background-color: rgba(0, 0, 0, 0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(2px);">
                            <svg height="24px" width="24px" version="1.1" viewBox="0 0 24 24"><path d="M8,5v14l11-7L8,5z" fill="#fff"></path></svg>
                        </div>
                    </div>
                </div>
            </a>

            <h3 class="mt-5 mb-4 fw-bold text-center">精選影片</h3>
            <div class="row g-4 justify-content-center">
              <div class="col-md-6">
                <a href="https://www.youtube.com/watch?v=QHV5WyFcBXQ" target="_blank" class="text-decoration-none d-block">
                    <div class="card h-100 shadow-sm border-0">
                      <div class="position-relative">
                          <div class="ratio ratio-16x9">
                            <img src="https://img.youtube.com/vi/QHV5WyFcBXQ/maxresdefault.jpg" class="w-100 h-100" style="object-fit: cover;" alt="惹味乾炒咖喱雞">
                          </div>
                          <div class="position-absolute top-50 start-50 translate-middle" style="z-index: 10;">
                              <div style="width: 56px; height: 56px; background-color: rgba(0, 0, 0, 0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(2px);">
                                  <svg height="24px" width="24px" version="1.1" viewBox="0 0 24 24"><path d="M8,5v14l11-7L8,5z" fill="#fff"></path></svg>
                              </div>
                          </div>
                      </div>
                      <div class="card-body text-center">
                        <h5 class="card-title fw-bold mt-2 text-dark">惹味乾炒咖喱雞</h5>
                        <p class="card-text text-muted small">咖喱控必學！星馬料理港式味道，香氣四溢。</p>
                      </div>
                    </div>
                </a>
              </div>
              <div class="col-md-6">
                <a href="https://www.youtube.com/watch?v=SU_CwTwxhpc" target="_blank" class="text-decoration-none d-block">
                    <div class="card h-100 shadow-sm border-0">
                      <div class="position-relative">
                          <div class="ratio ratio-16x9">
                            <img src="https://img.youtube.com/vi/SU_CwTwxhpc/maxresdefault.jpg" class="w-100 h-100" style="object-fit: cover;" alt="潮州鹵水五花腩">
                          </div>
                          <div class="position-absolute top-50 start-50 translate-middle" style="z-index: 10;">
                              <div style="width: 56px; height: 56px; background-color: rgba(0, 0, 0, 0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(2px);">
                                  <svg height="24px" width="24px" version="1.1" viewBox="0 0 24 24"><path d="M8,5v14l11-7L8,5z" fill="#fff"></path></svg>
                              </div>
                          </div>
                      </div>
                      <div class="card-body text-center">
                        <h5 class="card-title fw-bold mt-2 text-dark">潮州鹵水五花腩</h5>
                        <p class="card-text text-muted small">送飯必備！鹹香惹味，做法簡單又入味。</p>
                      </div>
                    </div>
                </a>
              </div>
            </div>
            """,
        },
        {
            'slug': 'food-review',
            'title': '美食評論',
            'content': """
            <h2>美食評論</h2>
            <p>王子熱愛嘗試新鮮美食，帶您走訪各地餐廳與市集，分享真實的味覺體驗。</p>
            """,
        },
        {
            'slug': 'recipes',
            'title': '新鮮食譜',
            'content': """
            <p>用簡單步驟做出好味道——重點在於火候與調味。把靈感落地到餐桌，天天都有新鮮感。</p>
            """,
        },
        {
            'slug': 'products',
            'title': '特色產品',
            'content': """
            <p>自家研製的調味，追求清晰的風味層次。少一點複雜，多一點恰到好處。</p>
            """,
        },
        {
            'slug': 'lifestyle',
            'title': '味覺足跡',
            'content': """
            <!-- Section 1: Lifestyle Intro (Hero) -->
            <section class="position-relative full-bleed d-flex align-items-end pb-5" style="background-image: url('/media/gallery/lifestyle-hero.jpg?v={int(time.time())}'); background-size: cover; background-position: center; min-height: 65vh;">
                <div class="position-absolute top-0 start-0 w-100 h-100" style="background: linear-gradient(to bottom, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.6) 100%);"></div>
                <div class="container position-relative z-index-2 mb-4">
                    <div class="row">
                        <div class="col-lg-8">
                            <div class="section-eyebrow text-warning mb-2">Lifestyle</div>
                            <h1 class="magazine-hero-title text-white mb-3">The Art of Living<br>生活風格</h1>
                            <p class="lead text-white opacity-90 mb-0" style="max-width: 600px;">Cooking is not only about food. It is a way of living. <br>料理從來不只是烹飪技巧，而是一種對生活細節的追求。</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Section 2: Travel (Editorial Split) -->
            <section class="py-5 full-bleed">
                <div class="container-fluid px-0">
                    <div class="row g-0 align-items-center">
                        <div class="col-lg-6">
                            <div class="ratio ratio-4x3">
                                <img src="/media/gallery/travel-hero.jpg?v={int(time.time())}" class="w-100 h-100" style="object-fit: cover;" alt="Travel & Inspiration" loading="lazy">
                            </div>
                        </div>
                        <div class="col-lg-6 p-4 p-lg-5 bg-white">
                            <div class="ps-lg-4">
                                <div class="section-eyebrow text-dark mb-3">Travel</div>
                                <h2 class="section-title display-5 mb-4">Travel & Inspiration<br>旅行與靈感</h2>
                                <p class="section-subtitle text-muted mb-4 fst-italic">"Each destination inspires the creativity behind GWZ."</p>
                                <div class="text-muted">
                                    <p class="drop-cap">世</p>
                                    <p>界各地的文化與風味，一直是王子料理創作的重要靈感來源。從倫敦到歐洲，從亞洲不同城市到各地市場，每一次旅行都帶來新的味道與想法。</p>
                                    <p class="mt-3">這些文化與體驗，慢慢地融入 GWZ 的料理風格之中。旅行不僅是移動，更是味覺的積累。</p>
                                </div>
                                """ + build_gallery_block(travel_set, "travel") + """
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Section 3: Market (Overlap Layout) -->
            <section class="py-5 bg-cream full-bleed position-relative overflow-hidden">
                <div class="container">
                    <div class="row align-items-center">
                        <div class="col-lg-6 order-lg-2">
                             <div class="ratio ratio-1x1 shadow-lg mb-4 mb-lg-0">
                                <img src="/media/gallery/market-hero.jpg" class="w-100 h-100" style="object-fit: cover;" alt="Markets" loading="lazy">
                            </div>
                        </div>
                        <div class="col-lg-6 order-lg-1">
                            <div class="pe-lg-5">
                                <div class="section-eyebrow text-dark">Market</div>
                                <h2 class="section-title mb-3">Markets & Ingredients<br>食材的起點</h2>
                                <p class="lead text-secondary mb-4">Great cooking begins with great ingredients.</p>
                                <div class="editorial-columns text-muted">
                                    <p>每一道好的料理，其實都從食材開始。王子喜歡親自到市場與超市挑選食材，了解食材的新鮮度、來源與品質。</p>
                                    <p>因為只有好的食材，才能做出真正有靈魂的料理。挑選食材的過程，本身就是與自然對話的開始。</p>
                                </div>
                                """ + build_gallery_block(market_set, "market") + """
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Section 4: Kitchen (Centered Editorial) -->
            <section class="py-5 bg-white full-bleed">
                <div class="container">
                    <div class="text-center mb-5 mx-auto" style="max-width: 800px;">
                        <div class="section-eyebrow text-dark">Kitchen</div>
                        <h2 class="section-title display-4 mb-3">The Kitchen Lab</h2>
                        <p class="section-subtitle text-muted">"Where creativity becomes flavour."</p>
                    </div>
                    
                    <div class="row justify-content-center mb-5">
                         <div class="col-lg-10">
                            <div class="ratio ratio-21x9 shadow-sm">
                                <img src="/media/gallery/kitchen-hero.jpg" class="w-100 h-100 rounded" style="object-fit: cover;" alt="Kitchen" loading="lazy">
                            </div>
                         </div>
                    </div>

                    <div class="row justify-content-center mb-4">
                        <div class="col-lg-8">
                            <div class="editorial-columns text-muted">
                                <p><span class="fw-bold text-dark">廚房，是王子最熟悉的地方。</span> 在這裡，食材、火候與經驗結合，創造出一道道料理。每一次烹飪，其實都是一次創作。</p>
                                <p>不論是實驗新的調味組合，還是重現經典的味道，廚房永遠充滿著無限的可能與驚喜。這是一個關於溫度、時間與耐心的實驗室。</p>
                            </div>
                        </div>
                    </div>
                    """ + build_gallery_block(kitchen_set, "kitchen") + """
                </div>
            </section>

            <!-- Section 5: Music (Dark Immersive) -->
            <section class="py-5 bg-charcoal full-bleed text-white">
                <div class="container">
                    <div class="row align-items-center g-5">
                        <div class="col-lg-5">
                            <div class="ratio ratio-1x1 shadow-soft border border-secondary">
                                <img src="/media/gallery/music-hero.jpg" class="w-100 h-100" style="object-fit: cover; filter: grayscale(20%);" alt="Music" loading="lazy">
                            </div>
                        </div>
                        <div class="col-lg-7">
                            <div class="ps-lg-5">
                                <div class="section-eyebrow text-warning">Music & Vibe</div>
                                <h2 class="section-title display-5 mb-4">Rhythm of Cooking<br>生活中的藝術</h2>
                                <p class="lead text-light opacity-75 mb-4">Cooking and music share the spirit of creativity.</p>
                                <p class="text-white-50">對王子而言，料理與音樂其實有很多相似的地方。節奏、平衡與情感，都在其中。音樂、藝術與生活體驗，都會影響料理的靈感與創意。當爵士樂響起，鍋中的律動也隨之起舞。</p>
                                """ + build_gallery_block(music_set, "music") + """
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Section 6: Moments (Gallery Focus) -->
            <section class="py-5 full-bleed position-relative" style="background-image: url('/media/gallery/moments-hero.jpg'); background-attachment: fixed; background-size: cover; min-height: 400px;">
                 <div class="position-absolute top-0 start-0 w-100 h-100" style="background: rgba(93, 46, 134, 0.9);"></div>
                 <div class="container position-relative z-index-2 py-5">
                    <div class="text-center text-white mb-4 mx-auto" style="max-width: 700px;">
                        <h2 class="magazine-hero-title mb-3">Moments</h2>
                        <p class="lead">Good food is meant to be shared.</p>
                        <p class="opacity-75">料理的真正意義，往往來自與人分享的時刻。朋友、家人、餐桌上的交流與笑聲，都是生活中最珍貴的片刻。</p>
                    </div>
                    """ + build_gallery_block(moments_set, "moments") + """
                 </div>
            </section>

            <!-- Final Quote -->
            <section class="py-5 bg-white full-bleed text-center">
                <div class="container">
                    <div class="mx-auto" style="max-width: 600px;">
                         <p class="display-6 font-serif fst-italic text-dark mb-3">"Cooking is a reflection of life."</p>
                         <div class="text-muted text-uppercase small letter-spacing-2">— Prince</div>
                    </div>
                </div>
            </section>
            """,
        },
        {
            'slug': 'terms',
            'title': '條款與細則',
            'content': """
            <h2>條款與細則</h2>
            <p>歡迎來到 GWZ 網上商店。在使用本網站之前，請仔細閱讀以下條款與細則。</p>
            
            <h3>1. 一般條款</h3>
            <p>本網站由 GWZ 營運。在整個網站中，「我們」是指 GWZ。GWZ 向您（使用者）提供本網站，包括本網站提供的所有資訊、工具和服務，條件是您接受此處所述的所有條款、細則、政策和聲明。</p>
            
            <h3>2. 線上商店條款</h3>
            <p>同意這些服務條款，即表示您在您居住的州或省至少已達到成年年齡。</p>
            <p>您不得將我們的產品用於任何非法或未經授權的目的，也不得在使用服務時違反您所在司法管轄區的任何法律（包括但不限於版權法）。</p>
            
            <h3>3. 產品與服務</h3>
            <p>我們已盡一切努力盡可能準確地顯示商店中出現的產品的顏色和圖像。我們不能保證您的電腦顯示器顯示的任何顏色都是準確的。</p>
            <p>我們保留限制向任何人、地理區域或司法管轄區銷售我們的產品或服務的權利。我們可能視情況行使此權利。</p>
            
            <h3>4. 價格與付款</h3>
            <p>產品價格如有更改，恕不另行通知。我們保留隨時修改或終止服務（或其任何部分或內容）的權利，恕不另行通知。</p>
            
            <h3>5. 退換貨政策</h3>
            <p>請參閱我們的退換貨政策頁面以獲取詳細資訊。</p>
            
            <h3>6. 個人資訊</h3>
            <p>您透過商店提交的個人資訊受我們的隱私權政策管轄。</p>
            
            <h3>7. 聯絡資訊</h3>
            <p>有關服務條款的問題應發送至我們的聯絡電子郵件。</p>
            """,
        },
        {
            'slug': 'privacy',
            'title': '隱私權政策',
            'content': """
            <h2>隱私權政策</h2>
            <p>GWZ 尊重您的隱私權並致力於保護您的個人資料。</p>
            
            <h3>我們收集的資訊</h3>
            <p>當您訪問本網站時，我們會自動收集有關您設備的某些資訊，包括有關您的網頁瀏覽器、IP 地址、時區以及安裝在您設備上的一些 Cookie 的資訊。</p>
            <p>此外，當您進行購買或嘗試透過本網站進行購買時，我們會收集您的某些資訊，包括您的姓名、帳單地址、送貨地址、付款資訊（包括信用卡號碼）、電子郵件地址和電話號碼。</p>
            
            <h3>我們如何使用您的資訊</h3>
            <p>我們通常使用我們收集的訂單資訊來完成透過本網站下的任何訂單（包括處理您的付款資訊、安排運輸以及向您提供發票和/或訂單確認）。</p>
            <p>此外，我們使用此訂單資訊來：</p>
            <ul>
                <li>與您溝通；</li>
                <li>篩選我們的訂單是否存在潛在風險或欺詐；以及</li>
                <li>根據您與我們分享的偏好，向您提供與我們的產品或服務相關的資訊或廣告。</li>
            </ul>
            
            <h3>資料保留</h3>
            <p>當您透過本網站下訂單時，除非您要求我們刪除此資訊，否則我們將保留您的訂單資訊作為我們的記錄。</p>
            """,
        },
        {
            'slug': 'story-sea-market',
            'title': '海邊市集的早晨',
            'content': """
            <div class="ratio ratio-16x9 mb-4">
                <img src="/static/img/88_seafood010.jpg" class="w-100 h-100 rounded" style="object-fit: cover;" alt="海邊市集的早晨">
            </div>
            <p class="lead">沿著海風走進市集，攤位上的新鮮漁獲與香草映出清晨的色彩。料理的靈魂，來自土地與海洋。</p>
            <p>挑幾樣最當季的魚與蔬菜，配上簡單的鹽與橄欖油，味道清晰而直接。當食材足夠新鮮，步驟就能更簡單——讓自然的風味站在前排。</p>
            <blockquote class="blockquote border-start ps-3 my-4">
                <p class="mb-0">「好吃的關鍵，往往不是複雜的技巧，而是對食材的尊重。」</p>
            </blockquote>
            <p>晚餐的輪廓在腦海中成形：以海味為主角，佐以當季蔬菜，火候與調味各退一步，讓食材自己說話。這就是旅途上帶回家的靈感。</p>
            <p><a class="btn btn-outline-dark rounded-pill px-4" href="/gallery/" rel="noopener">前往照片庫</a></p>
            """ + build_gallery_block(g1, "story-sea") + """
            """,
        },
        {
            'slug': 'story-coffee-ritual',
            'title': '咖啡的日常儀式',
            'content': """
            <p>磨豆、注水、等待香氣升起，是一天的開場。這份耐心也是料理的核心：尊重時間，尊重食材。</p>
            <p>一杯好咖啡的細節，像是火候與調味的拿捏——微小之處見真章。</p>
            <p><a class="btn btn-outline-dark rounded-pill px-4" href="/gallery/" rel="noopener">前往照片庫</a></p>
            """ + build_gallery_block(g2, "story-coffee") + """
            """,
        },
        {
            'slug': 'story-street-food',
            'title': '街角的風味',
            'content': """
            <p>街邊攤的炊煙與香料氣息，是城市的味覺記憶。快速、熱烈、直接——有時候最令人難忘的風味，來自最純粹的手藝。</p>
            <p>把這些靈感帶回廚房，試試以家常的方式重現那份自由。</p>
            <p><a class="btn btn-outline-dark rounded-pill px-4" href="/gallery/" rel="noopener">前往照片庫</a></p>
            """ + build_gallery_block(g3, "story-street") + """
            """,
        },
    ]
    
    for pd in pages_data:
        page, created = Page.objects.get_or_create(slug=pd['slug'])
        page.title = pd['title']
        page.content = pd['content']
        page.is_active = True
        page.save()
        print(f"Page '{pd['slug']}' created/updated.")

if __name__ == "__main__":
    update_content()
