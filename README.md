# EV CRM Backend (Django + DRF)

Covers every module from the requirement docs: E-commerce product catalog with hidden pricing,
Vendor onboarding/approval, Battery + Batch + QR management, Scooter management, Customers,
Coupons, and the full Sales CRM (Leads, Pipeline, Follow-ups, Quotations, Tasks, Notifications).

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py shell < seed.py     # creates admin user + pipeline stages + lead sources
python manage.py runserver
```

Login: **admin / Admin@123** (change immediately in production)

Admin panel: http://localhost:8000/admin/
API root: http://localhost:8000/api/

## Auth

JWT via `djangorestframework-simplejwt`.

```
POST /api/auth/login/    { "username": "...", "password": "..." }  -> { access, refresh }
POST /api/auth/refresh/  { "refresh": "..." }                       -> { access }
```

Send `Authorization: Bearer <access>` on every other request.

## Apps / Endpoint map

| App        | Base path                          | Covers |
|------------|-------------------------------------|--------|
| accounts   | /api/users/, /api/sales-targets/    | Admin/Sales/Vendor users, roles, sales targets |
| vendors    | /api/vendors/, /api/vendor-documents/ | Registration, onboarding, approval actions (`/approve/`, `/reject/`, `/suspend/`, `/activate/`, `/request_changes/`), documents, status + activity history |
| products   | /api/products/, /api/public-products/, /api/vendor-product-prices/ | Catalog, vendor-specific pricing, public listing (price hidden unless an approved vendor is attached) |
| battery    | /api/battery-batches/, /api/batteries/ | Batch creation, `/generate_batteries/` (batch-wise auto numbering), `/change_status/`, `/generate_qr/` |
| scooters   | /api/scooters/                     | Add/edit, `/assign_battery/`, `/replace_battery/` (keeps history) |
| customers  | /api/customers/, /api/customer-documents/ | Customer profile + documents |
| coupons    | /api/coupons/                      | Coupon generation + history + status |
| crm        | /api/leads/, /api/pipeline-stages/, /api/lead-sources/, /api/follow-ups/, /api/quotations/, /api/quotation-items/, /api/tasks/, /api/notifications/, /api/dashboard-summary/ | Full Sales CRM: leads, pipeline stages (drag & drop via `/change_stage/`), duplicate detection, lost/reopen, conversion to customer, follow-ups (today/overdue/upcoming), quotations with revisions, tasks, notifications, dashboard KPIs |

All list endpoints support `?search=`, filtering (see `filterset_fields` per view) and DRF pagination.

## Notes on business rules implemented

- Product price is `null` for anonymous/non-approved-vendor requests on `/api/public-products/`.
- Every vendor status change is recorded in `VendorStatusHistory` + `VendorActivity` (powers the vendor timeline).
- `generate_batteries` on a batch creates individually-numbered batteries (Battery 001..N) with unique serials.
- Every battery status change is recorded in `BatteryStatusHistory`.
- Scooter battery replacement keeps the old `ScooterBatteryHistory` row (with `removed_on`) instead of deleting it.
- Coupon `created_by` is always recorded and shown in coupon history.
- Lead creation does simple duplicate detection by mobile number (`is_duplicate_of`).

## Extending

This is a complete, working foundation — every model/table from both requirement documents
is represented and reachable through the REST API + Django admin. From here, typical next steps:
add role-based permission classes per viewset, wire real WhatsApp/Email/SMS providers into
`FollowUp`/`Notification`, and add Celery for reminders.
