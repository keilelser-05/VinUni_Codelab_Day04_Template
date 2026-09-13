import json
import os
from typing import List, Dict, Any
from datetime import datetime

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "raw-data")

# ---------------------------------------------------------------------------
# Tool #1: search_product_catalog
# TODO: Hoàn thiện hàm này — đọc file product_catalog.json, lọc theo category và max_price.
# ---------------------------------------------------------------------------

def search_product_catalog(category: str, max_price: int = 999999999999):
    if not isinstance(category, str) or category.lower() not in ("xe_dien", "du_lich"):
        raise ValueError("Danh mục phải là xe_dien hoặc du_lich.")
    if type(max_price) is not int or max_price < 0:
        raise ValueError("max_price phải là số nguyên không âm.")
    with open(Path(RAW_DATA_DIR) / "product_catalog.json", encoding="utf-8") as f:
        products = json.load(f)
    if not isinstance(products, list):
        raise ValueError("Catalog phải là danh sách JSON.")
    return [p for p in products if p["category"].lower() == category.lower()
            and p["price_vnd"] <= max_price]


# ---------------------------------------------------------------------------
# Tool #2: submit_support_ticket
# TODO: Hoàn thiện hàm này — tạo ticket mới và lưu vào support_tickets.json.
# ---------------------------------------------------------------------------

def submit_support_ticket(customer_name: str, issue_description: str, priority: str = "medium"):
    if not isinstance(customer_name, str) or not customer_name.strip():
        raise ValueError("Thiếu tên khách hàng.")
    if not isinstance(issue_description, str) or not issue_description.strip():
        raise ValueError("Thiếu mô tả vấn đề.")
    if not isinstance(priority, str) or priority.lower() not in ("low", "medium", "high"):
        raise ValueError("Priority không hợp lệ.")
    path = Path(RAW_DATA_DIR) / "support_tickets.json"
    with _LOCK:
        tickets = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        if not isinstance(tickets, list):
            raise ValueError("Tickets phải là danh sách JSON; không ghi đè dữ liệu lỗi.")
        now = datetime.now(timezone(timedelta(hours=7)))
        prefix = f"TK-{now:%Y%m%d}-"
        ids = {str(t.get("ticket_id", "")) for t in tickets}
        seq = max([int(i[len(prefix):]) for i in ids
                   if i.startswith(prefix) and i[len(prefix):].isdigit()] + [0]) + 1
        ticket = dict(ticket_id=f"{prefix}{seq:03d}", customer_name=customer_name.strip(),
                      issue_description=issue_description.strip(), priority=priority.lower(),
                      status="open", created_at=now.isoformat(), category="general")
        tickets.append(ticket)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                             delete=False, suffix=".tmp") as f:
                temporary = f.name
                json.dump(tickets, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary, path)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
    return {**ticket, "message": f"Ticket {ticket['ticket_id']} đã được tạo thành công."}


# ---------------------------------------------------------------------------
# TOOL_DEFINITIONS — JSON Schemas mô tả cho LLM
# TODO: Định nghĩa JSON Schema cho từng tool (name, description, parameters).
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    # TODO: Thêm schema cho "search_product_catalog"
    # TODO: Thêm schema cho "submit_support_ticket"
]


# ---------------------------------------------------------------------------
# TOOL_MAP — Ánh xạ tên tool → hàm thực thi
# ---------------------------------------------------------------------------

TOOL_MAP = {
    "search_product_catalog": search_product_catalog,
    "submit_support_ticket": submit_support_ticket
}
