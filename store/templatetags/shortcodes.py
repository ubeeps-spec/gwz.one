from django import template
import re

register = template.Library()

def _render_cards3(attrs: str, body: str) -> str:
    title = ""
    m = re.search(r'title="([^"]*)"', attrs or "")
    if m:
        title = m.group(1)
    
    # Try to parse list items <li>...</li>
    items = re.findall(r'<li[^>]*>(.*?)</li>', body or "", flags=re.S | re.I)
    
    # If no <li> found, try splitting by newlines and looking for "- " or simple lines
    if not items:
        # Remove empty lines
        lines = [x.strip() for x in (body or "").splitlines() if x.strip()]
        # Remove bullet points if present
        items = []
        for x in lines:
            # Check for common bullet characters
            if x.startswith(('-', '*', '•')):
                # Remove the bullet and leading/trailing whitespace
                clean_x = re.sub(r'^[-*•]\s*', '', x)
                items.append(clean_x)
            else:
                items.append(x)
                
    items = items[:3]
    
    # Define some icons/colors for the 3 cards to make them distinct but cohesive
    # This is a simple rotation logic
    card_configs = [
        {'icon': 'bi-heart', 'bg': 'bg-light', 'border': 'border-0'},
        {'icon': 'bi-star', 'bg': 'bg-light', 'border': 'border-0'},
        {'icon': 'bi-lightbulb', 'bg': 'bg-light', 'border': 'border-0'}
    ]
    
    cards_html_list = []
    for i, it in enumerate(items):
        cfg = card_configs[i % 3]
        
        # Try to split item into Title and Text if possible (e.g. "Title: Text")
        item_title = ""
        item_text = it
        if ":" in it:
            parts = it.split(":", 1)
            item_title = parts[0].strip()
            item_text = parts[1].strip()
        elif "：" in it:
             parts = it.split("：", 1)
             item_title = parts[0].strip()
             item_text = parts[1].strip()
        
        title_block = f'<h5 class="card-title fw-bold mb-3" style="color: var(--primary-purple);">{item_title}</h5>' if item_title else ''
        
        cards_html_list.append(f'''
        <div class="col-md-4">
          <div class="card h-100 {cfg['border']} shadow-sm hover-lift transition-all">
            <div class="card-body text-center p-4">
              <div class="mb-3">
                 <span class="d-inline-flex align-items-center justify-content-center bg-white rounded-circle shadow-sm" style="width: 60px; height: 60px; color: var(--primary-purple);">
                    <i class="bi {cfg['icon']} fs-3"></i>
                 </span>
              </div>
              {title_block}
              <div class="card-text text-muted">{item_text}</div>
            </div>
          </div>
        </div>
        ''')

    cards_html = "".join(cards_html_list)
    title_html = f'<h2 class="fw-bold text-center mb-5 display-6">{title}</h2>' if title else ''
    
    return f'''
    <div class="container my-5 py-5">
      {title_html}
      <div class="row g-4 justify-content-center">
        {cards_html}
      </div>
    </div>
    '''

@register.filter
def render_shortcodes(value: str) -> str:
    if not isinstance(value, str):
        return value
    def repl_cards3(m):
        return _render_cards3(m.group(1), m.group(2))
    pattern_cards3 = re.compile(r'\[cards3(.*?)\](.*?)\[/cards3\]', re.S | re.I)
    value = pattern_cards3.sub(repl_cards3, value)
    return value
