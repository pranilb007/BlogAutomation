# Safe colorama import for CLI output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # fallback if colorama not installed
    class _Dummy:
        def __getattr__(self, _):
            return ""
    Fore = _Dummy()
    Style = _Dummy()

# create_blog_via_api_with_docx.py
from lxml import etree
import requests, docx, re, os
from requests.auth import HTTPBasicAuth
from docx.oxml.ns import qn
from dotenv import load_dotenv

# ---- CONFIG: adjust as needed ----
# base_url  = "http://website1.local.com/"
# username  = "Pranil"
# password  = "Pranil@8998#"
# password = "bUhT$$7Suy2+TeTW"

load_dotenv()  

base_url = os.getenv("DRUPAL_BASE_URL")
username = os.getenv("DRUPAL_USERNAME")
password = os.getenv("DRUPAL_PASSWORD")
auth = HTTPBasicAuth(username, password)
headers = {"Content-Type": "application/vnd.api+json"}

# --- Replace with real UUIDs ---
CATEGORY_UUIDS = {
    "Strategy": "8383cd40-f697-4645-98e0-d9d84a353aac",
    "M&A": "6d0739b1-e375-46ee-8704-b2598b4d70af",
    "Procurement Strategy": "7ba30f75-7107-4ebc-9cfb-89c8e69a9bca",
    "Automation": "61aa3856-48a5-4ba6-b62e-6d970b877b5c",
    "Inventory Management": "142944d2-1c8c-4982-a74b-3b24acabd12a",
    "Cost Management": "bd8264aa-212b-46f8-948b-5fd9932f245f",
    "Digital Supply Chain Transformation": "c3fca0f1-99b0-4139-b4fd-eaa53be38100",
    "Miscellaneous": "db6b187d-c701-4207-9dfa-c3433872430f",
    "Risk Management": "1f951848-b393-4a4d-be7e-915bc34ef451",
    "Sourcing Strategy": "3f445925-8109-416f-89d5-a47ee2fd7ed3",
    "Supplier Management Strategy": "6bd034f8-68b6-4f19-bf82-5461f857d6d8",
    "Supply Chain Risk Management": "7abc68d4-f6db-440f-8431-831446dc6794",
    "Supply Chain Strategy": "3f6cabeb-8fd6-47ce-8b2b-7ddd840d18ac",
    "Market Intelligence": "4770de65-592e-41ae-b3c7-e930ed539469",
    "Agro": "2a57b8e2-d4f7-46bd-8e6c-4e22ac31a6fe",
    "Automotives": "61870e69-7954-46cd-92e5-ace6c6fde027",
    "Awards and Events": "794f5cab-2c2a-4073-aeaa-8cf52c30702b",
    "Corporate Travel": "912b787d-df11-4df3-8658-197899f3e1c6",
    "CAPEX": "4e094e26-5aaa-44ef-b611-132f96cf6d4d",
    "Category Management": "0aa64a81-7273-4523-991a-3b9abb4c1bc5",
    "Chemicals": "640001c4-ea34-4366-9096-82236a275a77",
    "Direct Materials": "ec0bc2bb-3d09-494d-afa0-85841b9a9d0a",
    "Energy & Utilities": "4d93146d-6e96-45e8-8398-94a0a5b8bbc9",
    "Human Resource": "f5f7230b-65a7-4586-829d-1c450193935c",
    "Healthcare": "36399c68-661b-4f7f-8d05-d00b398642ec",
    "IT & Telecom": "43eba58e-d828-4cab-9bb7-36c2ba797562",
    "Logistics": "0a3e40c5-a2ff-4d20-bd47-1c7e9006805c",
    "Market Intelligence": "4770de65-592e-41ae-b3c7-e930ed539469",
    "Metals & Minerals": "f4cb6cc6-7032-4fd4-a993-3d0ea62e604a",
    "Marketing": "86831ee8-23e9-4355-b489-dcf9c87bece8",
    "MRO": "938ab3dd-27ac-43f6-bf4e-df88c7ed39f5",
    "Packaging": "a8e9c06a-5df2-4a31-a566-b07bdda7478f",
    "Pharma and Life Sciences": "88687365-b135-4354-90e0-0def4543ca9c",
    "Procurement Process and Excellence": "59e1bdf2-175e-4bab-999a-218bd65588d6",
    "Professional Services": "95b9861f-152a-46a5-9957-7440da5c6b16",
    "Supply Chain": "d43c163b-4f05-4ff9-9645-0cedd8d2dc79",
    "Oil and Gas": "363e567d-c34d-4fa4-8abd-212a48b14520",
    "Vendor Management": "adf3e75a-35a1-4712-a330-df8ef36d866d",
    "Technology": "ee1dfca6-dc6d-4844-9c13-48b890e38d63",
    "Technology 2": "aea6bece-fca7-4f69-9fca-5230ba38bfa4",
    "Accounts Payable": "60686582-9f4f-45e3-8601-648b2456ff1d",
    "Procurement Software": "b17b7b41-1327-4880-8331-b62dd7ffe153",
    "Contract Management": "acc1bf94-7400-47f8-9d3e-c3cd1e4079b2",
    "Inventory Management Software": "f8f81ec7-5759-47ac-bfad-6a39b4239b64",
    "Mobile and Cloud": "e261f1a6-3c4f-41b6-932f-018bc88fb136",
    "Operations": "d555da8d-6769-43c1-b5a8-667272d3dab7",
    "Source to Pay": "9ed02f55-ed49-4322-ae81-d26b5da8c0ce",
    "Purchasing": "a1fe52e3-3733-4823-b513-62086fa11aa2",
    "Procure to Pay": "0d5aacd8-9f36-431f-a7bb-e2a9212efb06",
    "Sourcing Technology": "7b8f8253-06a4-4025-9a9e-271ba6e32e0a",  
}
KB_UUIDS = {
    "Technology":  "807749d7-a44e-4844-85ed-a83a303dccad",
    "Procurement": "bbc3191e-f97d-4bb6-9221-889e2693ce5e",
    "Strategy and Planning": "fe80d829-5e33-4ee6-bd48-dec19d3d9ed5",
    "Digital Transformation": "ab695d16-6107-4c14-a1cd-2bc35ef34d52",
    "Artificial Intelligence": "a60dffc4-fdc3-4a8a-9352-fd6ae640ca5e",
    "Operations": "8281cf28-da33-43f1-b227-3537ebc44fe9",
    "Software and Technology": "1b72d2d5-18b1-4b61-b36c-5b550e6cda8a",
    "Sustainability": "ac89f046-e090-4446-b9a0-7cfadd8c1405",
    "Technology and Software": "502716e9-721c-466b-bcf1-b9b38fa2b52b",
}

# ---------- helpers ----------
def ensure_tag(tag_name):
    r = requests.get(f"{base_url}/jsonapi/taxonomy_term/blog_tags?filter[name]={tag_name}",
                     auth=auth, headers=headers)
    data = r.json()
    if data.get("data"):
        return data["data"][0]["id"]
    payload = {"data": {"type": "taxonomy_term--blog_tags",
                        "attributes": {"name": tag_name}}}
    r = requests.post(f"{base_url}/jsonapi/taxonomy_term/blog_tags",
                      json=payload, auth=auth, headers=headers)
    r.raise_for_status()
    return r.json()["data"]["id"]

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def para_to_html(para):
    html = ""
    xml = etree.fromstring(para._element.xml.encode("utf-8"))
    for child in xml:
        tag = etree.QName(child).localname
        if tag == "hyperlink":
            r_id = child.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            link_text = "".join(child.xpath('.//w:t/text()', namespaces=child.nsmap))
            if r_id and r_id in para.part.rels:
                target = para.part.rels[r_id].target_ref
                html += f'<a href="{target}">{link_text}</a>'
            else:
                html += link_text
        else:
            html += "".join(child.xpath('.//w:t/text()', namespaces=child.nsmap))
    return html

def render_cta(h, t, b, u):
    return f"""
<div class="promo-box-primary p-4 mt-5 mb-5">
  <div class="container">
    <div class="row justify-content-center text-center">
      <div class="col-md-12 col-12">
        <h3>{h}</h3>
        <p>{t}</p>
        <p><a class="btn btn-secondary mb-2 mb-md-0" href="{u}">{b}</a></p>
      </div>
    </div>
  </div>
</div>
"""

def find_image_by_suffix(images_dir, slug, suffix):
    pattern = re.compile(fr".*-{re.escape(suffix)}\.(jpg|jpeg|png|gif)$", re.IGNORECASE)
    for f in os.listdir(images_dir):
        if pattern.match(f):
            return os.path.join(images_dir, f)
    # not found
    return None

def upload_image(path, field_endpoint):
    """
    Upload image to Drupal by using the node field upload endpoint.
    Returns file UUID.
    """
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    fname = os.path.basename(path)
    url   = f"{base_url}/jsonapi/node/blog_posts/{field_endpoint}"
    headers_img = {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": f'file; filename="{fname}"'
    }
    with open(path, "rb") as f:
        r = requests.post(url, headers=headers_img, data=f, auth=auth)
    r.raise_for_status()
    return r.json()["data"]["id"]

# ---------- main function ----------
def create_blog(docx_path, images_dir):
    """Main entry: parse docx, upload images found in images_dir and create node.
       Returns requests.Response from node creation (so caller can inspect status).
    """
    doc = docx.Document(docx_path)

    # variables
    title = None
    body_html = ""
    bullets_html = ""
    inside_list = False
    first_bullet_list_done = False
    tags = []
    categories = []
    kb_categories = []
    asset_id = None
    custom_url = None

    # regex
    cat_re   = re.compile(r"^Categories:\s*(.+)$", re.I)
    tag_re   = re.compile(r"^Tags:\s*(.+)$", re.I)
    kb_re    = re.compile(r"^KB\s*Category:\s*(.+)$", re.I)
    asset_re = re.compile(r"^Asset\s*ID:\s*(.+)$", re.I)
    url_re   = re.compile(r"^URL:\s*(.+)$", re.I)
    cta_heading_re = re.compile(r"^CTA\s*Heading:\s*(.+)$", re.I)
    cta_text_re    = re.compile(r"^CTA\s*Text:\s*(.+)$", re.I)
    cta_btn_re     = re.compile(r"^CTA\s*Button:\s*(.+)$", re.I)
    cta_url_re     = re.compile(r"^CTA\s*URL:\s*(.+)$", re.I)

    cta_h = cta_t = cta_b = cta_u = None

    # parse paragraphs
    for para in doc.paragraphs:
        plain = para.text.strip()
        html_text = para_to_html(para).strip()
        if not plain:
            continue

        # metadata
        if m := url_re.match(plain):
            custom_url = m.group(1).strip(); continue
        if m := asset_re.match(plain):
            asset_id = m.group(1).strip(); continue
        if m := cat_re.match(plain):
            categories = [c.strip() for c in m.group(1).split(",")]; continue
        if m := tag_re.match(plain):
            tags = [t.strip() for t in m.group(1).split(",")]; continue
        if m := kb_re.match(plain):
            kb_categories = [k.strip() for k in m.group(1).split(",")]; continue

        # CTA
        if m := cta_heading_re.match(plain): cta_h = m.group(1).strip(); continue
        if m := cta_text_re.match(plain):    cta_t = m.group(1).strip(); continue
        if m := cta_btn_re.match(plain):     cta_b = m.group(1).strip(); continue
        if m := cta_url_re.match(plain):     cta_u = m.group(1).strip(); continue

        if all([cta_h, cta_t, cta_b, cta_u]):
            body_html += render_cta(cta_h, cta_t, cta_b, cta_u)
            cta_h = cta_t = cta_b = cta_u = None

        # content
        style = para.style.name
        if style.startswith("Heading 1") and title is None:
            title = plain
        elif style.startswith("Heading 2"):
            body_html += f"<h2>{html_text}</h2>\n"
        elif style.startswith("Heading 3"):
            body_html += f"<h3>{html_text}</h3>\n"
        elif style.startswith("Heading 4"):
            body_html += f"<h4>{html_text}</h4>\n"
        elif style == "List Paragraph":
            if not first_bullet_list_done:
                if not inside_list:
                    bullets_html += "<ul>\n"; inside_list = True
                bullets_html += f"  <li>{html_text}</li>\n"
            else:
                body_html += f"<ul><li>{html_text}</li></ul>\n"
        else:
            if inside_list and not first_bullet_list_done:
                bullets_html += "</ul>\n"
                inside_list = False; first_bullet_list_done = True
            body_html += f"<p>{html_text}</p>\n"

    if inside_list and not first_bullet_list_done:
        bullets_html += "</ul>\n"; first_bullet_list_done = True
    if not title:
        title = "Untitled Blog"
    if all([cta_h, cta_t, cta_b, cta_u]):
        body_html += render_cta(cta_h, cta_t, cta_b, cta_u)

    # slug and relationships
    slug = slugify(title)
    rels = {}
    if tags:
        rels["field_blog_tags"] = {
            "data": [{"type": "taxonomy_term--blog_tags", "id": ensure_tag(t)} for t in tags]
        }
    if categories:
        if len(categories) > 1: raise ValueError(f"Only one Blog Category allowed: {categories}")
        c = categories[0]
        if c in CATEGORY_UUIDS:
            rels["field_blog_categories"] = {
                "data": [{"type": "taxonomy_term--blog_categories", "id": CATEGORY_UUIDS[c]}]
            }
        else: raise ValueError(f"Unknown Blog Category: {c}")
    if kb_categories:
        if len(kb_categories) > 1: raise ValueError(f"Only one KB Category allowed: {kb_categories}")
        k = kb_categories[0]
        if k in KB_UUIDS:
            rels["field_kb_category"] = {
                "data": [{"type": "taxonomy_term--knowledge_bank", "id": KB_UUIDS[k]}]
            }
        else: raise ValueError(f"Unknown KB Category: {k}")

    # --- find and upload images using slug + suffix approach ---
    # returns None if not found; attach only if found
    blog_img_path = find_image_by_suffix(images_dir, slug, "J")
    og_img_path   = find_image_by_suffix(images_dir, slug, "I")
    latest_path   = find_image_by_suffix(images_dir, slug, "D")
    kb_banner     = find_image_by_suffix(images_dir, slug, "C")

    def maybe_upload(path, field_name):
        if path:
            file_uuid = upload_image(path, field_name)
            return file_uuid
        return None

    try:
        blog_uuid = maybe_upload(blog_img_path, "field_blog_image")
        og_uuid   = maybe_upload(og_img_path, "field_open_graph_image")
        latest_uuid = maybe_upload(latest_path, "field_latest_insights_image")
        kb_uuid = maybe_upload(kb_banner, "field_kb_hero_banner_image")
    except Exception as e:
        raise

    if blog_uuid:
        rels["field_blog_image"] = {"data": {"type": "file--file", "id": blog_uuid, "meta": {"alt": title}}}
    if og_uuid:
        rels["field_open_graph_image"] = {"data": {"type": "file--file", "id": og_uuid, "meta": {"alt": title}}}
    if latest_uuid:
        rels["field_latest_insights_image"] = {"data": {"type": "file--file", "id": latest_uuid, "meta": {"alt": title}}}
    if kb_uuid:
        rels["field_kb_hero_banner_image"] = {"data": {"type": "file--file", "id": kb_uuid, "meta": {"alt": title}}}

    # node payload
    attributes = {
        "title": title,
        "body": {"value": body_html, "format": "full_html"},
        "field_blog_bullets": {"value": bullets_html, "format": "basic_html"},
    }
    if asset_id:
        attributes["field_asset_id"] = asset_id
    if custom_url:
        attributes["path"] = {"alias": custom_url, "langcode": "en"}
    else:
        attributes["path"] = {"alias": f"/blogs/auto/{slug}", "langcode": "en"}

    payload = {
        "data": {
            "type": "node--blog_posts",
            "attributes": attributes,
            "relationships": rels
        }
    }

    r = requests.post(f"{base_url}/jsonapi/node/blog_posts",
                      json=payload, auth=auth, headers=headers)
    # return response for caller
    return r

# create_blog_via_api_with_docx_refactored.py

def format_blog_response(resp):
    """
    Format the blog creation response into a clean, readable dictionary
    Returns: dict with formatted response data
    """
    result = {
        "status_code": resp.status_code,
        "success": False,
        "message": "",
        "data": {}
    }
    
    # Check HTTP status first
    if resp.status_code >= 400:
        result["message"] = f"Error: HTTP {resp.status_code}"
        try:
            error_data = resp.json()
            if "errors" in error_data:
                errors = []
                for err in error_data["errors"]:
                    errors.append({
                        "title": err.get('title', 'Unknown error'),
                        "detail": err.get('detail', '')
                    })
                result["data"]["errors"] = errors
            else:
                result["data"] = error_data
        except Exception:
            result["data"]["raw_response"] = resp.text[:500]
        return result
    
    # Success cases
    result["success"] = True
    try:
        data = resp.json()
        
        # Check if node was created successfully
        if "data" in data and isinstance(data["data"], dict):
            node = data["data"]
            attrs = node.get("attributes", {})
            
            result["message"] = "Blog created successfully"
            result["data"] = {
                "title": attrs.get('title', 'N/A'),
                "node_id": node.get('id', 'N/A'),
                "status": 'Published' if attrs.get('status') else 'Draft',
                "created": attrs.get('created', 'N/A'),
                "url_path": attrs.get('path', {}).get('alias', 'N/A') if 'path' in attrs else 'N/A'
            }
            
        elif "data" in data and isinstance(data["data"], list):
            result["message"] = f"{len(data['data'])} item(s) processed"
            result["data"]["items"] = []
            for item in data["data"][:10]:  # Show first 10
                result["data"]["items"].append({
                    "title": item.get("attributes", {}).get("title", "N/A"),
                    "id": item.get("id", "N/A")
                })
        else:
            result["message"] = "Request completed"
            result["data"]["summary"] = {k: type(v).__name__ for k, v in data.items()}
    
    except Exception as e:
        result["message"] = f"Warning: Could not parse response - {str(e)}"
        result["data"]["raw_preview"] = resp.text[:200]
    
    return result


# CLI support
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Upload blog via Drupal JSON:API")
    parser.add_argument("--docx", required=True, help="Path to .docx file")
    parser.add_argument("--images", required=True, help="Path to images directory")
    args = parser.parse_args()
    
    resp = create_blog(args.docx, args.images)
    result = format_blog_response(resp)
    
    print("\n" + "="*60)
    print("BLOG UPLOAD RESULT")
    print("="*60)
    
    if result["success"]:
        print(f"\n✅ {result['message']}\n")
        for key, value in result["data"].items():
            if isinstance(value, dict):
                print(f"\n{key.upper()}:")
                for k, v in value.items():
                    print(f"  {k.replace('_', ' ').title():<15}: {v}")
            elif isinstance(value, list):
                print(f"\n{key.upper()}:")
                for idx, item in enumerate(value, 1):
                    print(f"  {idx}. {item}")
            else:
                print(f"{key.replace('_', ' ').title():<15}: {value}")
    else:
        print(f"\n❌ {result['message']}\n")
        if "errors" in result["data"]:
            for err in result["data"]["errors"]:
                print(f"  • {err['title']}")
                if err['detail']:
                    print(f"    {err['detail']}")
        else:
            print(json.dumps(result["data"], indent=2))
    
    print("\n" + "="*60 + "\n")