# SmallBadge: Digital Badge Issuing & Verification Platform
## Phase 3: Database Design (MongoDB Schemas)

---

## 1. Why MongoDB for SmallBadge?
For this project, we choose **MongoDB** (a NoSQL document database) over traditional Relational Database Management Systems (like MySQL or PostgreSQL). In your project viva, you should justify this choice with these points:
* **JSON-Like Documents (BSON)**: MongoDB stores data in documents that match python dictionaries naturally, eliminating the complex Object-Relational Mapping (ORM) overhead.
* **Flexible Schemas**: Badge templates and metadata structures can evolve without needing database migrations.
* **High Performance**: Read operations (essential for badge verification searches) are extremely fast.

---

## 2. Collections and Schema Design

Here are the collection specifications, their relationships, and sample documents.

### 2.1 Users Collection (`users`)
* **Purpose**: Manages credentials, roles, and status for all active individuals.
* **Relationships**: Organizations are linked via `org_id` (one-to-one or one-to-many relationship).

```json
{
  "_id": "ObjectId('60d5ec49f1a2c34b88888801')",
  "name": "Prof. Amit Kumar",
  "email": "amit.kumar@college.edu",
  "password_hash": "$2b$12$K3d8g...", 
  "role": "org_admin", 
  "org_id": "ObjectId('60d5ec49f1a2c34b88888802')", 
  "status": "active", 
  "created_at": "2026-07-18T14:10:00Z"
}
```

### 2.2 Organizations Collection (`organizations`)
* **Purpose**: Tracks institutes seeking to issue digital badges.
* **Relationships**: Links to users (admins) and courses.

```json
{
  "_id": "ObjectId('60d5ec49f1a2c34b88888802')",
  "name": "National Institute of Technology",
  "domain": "nit.edu",
  "contact_phone": "+91-9876543210",
  "address": "New Delhi, India",
  "logo_url": "/static/uploads/logos/nit_logo.png",
  "status": "approved", // Options: "pending", "approved", "suspended"
  "created_at": "2026-07-18T14:05:00Z"
}
```

### 2.3 Courses Collection (`courses`)
* **Purpose**: Registers programs, courses, or events for which badges are issued.
* **Relationships**: Belongs to an organization via `org_id`.

```json
{
  "_id": "ObjectId('60d5ec49f1a2c34b88888803')",
  "org_id": "ObjectId('60d5ec49f1a2c34b88888802')",
  "course_code": "MCA-202",
  "course_name": "Web Application Architecture",
  "description": "Advanced server systems using Python and Flask.",
  "created_at": "2026-07-18T14:15:00Z"
}
```

### 2.4 Students Collection (`students`)
* **Purpose**: Stores student profiles enrolled under different organizations.
* **Relationships**: Linked to an organization via `org_id`.

```json
{
  "_id": "ObjectId('60d5ec49f1a2c34b88888804')",
  "org_id": "ObjectId('60d5ec49f1a2c34b88888802')",
  "name": "Rahul Sharma",
  "email": "rahul.sharma@student.nit.edu",
  "roll_number": "MCA/2024/042",
  "created_at": "2026-07-18T14:20:00Z"
}
```

### 2.5 Badge Templates Collection (`badge_templates`)
* **Purpose**: Defines visual layouts and template metadata for generation.
* **Relationships**: Belongs to an organization via `org_id`.

```json
{
  "_id": "ObjectId('60d5ec49f1a2c34b88888805')",
  "org_id": "ObjectId('60d5ec49f1a2c34b88888802')",
  "title": "Elite Web Developer Badge",
  "badge_description": "Awarded for exceptional performance in advanced web architecture.",
  "bg_image_path": "/static/uploads/templates/elite_developer_bg.png",
  "font_color": "#1a252f",
  "border_color": "#f1c40f",
  "created_at": "2026-07-18T14:25:00Z"
}
```

### 2.6 Issued Badges Collection (`issued_badges`)
* **Purpose**: Tracks actual issued credentials.
* **Relationships**:
  * Links to `student_id` (Student)
  * Links to `course_id` (Course)
  * Links to `template_id` (Badge Template)
  * Links to `org_id` (Organization)
* **Fields**:
  * `badge_id`: A unique string hash (e.g., SHA-256) used for verification URLs.
  * `status`: "issued" or "revoked".

```json
{
  "_id": "ObjectId('60d5ec49f1a2c34b88888806')",
  "badge_id": "b3d5e8f81a7d620fc1184a44b1c2b5f6e872c679a9ef229048a1cd99e3a6c52a",
  "org_id": "ObjectId('60d5ec49f1a2c34b88888802')",
  "student_id": "ObjectId('60d5ec49f1a2c34b88888804')",
  "course_id": "ObjectId('60d5ec49f1a2c34b88888803')",
  "template_id": "ObjectId('60d5ec49f1a2c34b88888805')",
  "issued_date": "2026-07-18T14:30:00Z",
  "qr_code_path": "/static/uploads/qrcodes/b3d5e8f8.png",
  "pdf_path": "/static/uploads/pdfs/b3d5e8f8.pdf",
  "status": "issued", 
  "revoked_reason": null
}
```

### 2.7 Activity Logs Collection (`activity_logs`)
* **Purpose**: Audit trails for platform modifications and security compliance.

```json
{
  "_id": "ObjectId('60d5ec49f1a2c34b88888807')",
  "timestamp": "2026-07-18T14:31:00Z",
  "user_id": "ObjectId('60d5ec49f1a2c34b88888801')",
  "role": "org_admin",
  "action": "ISSUE_BADGE",
  "details": "Issued badge 'MCA-202' to student Rahul Sharma (rahul.sharma@student.nit.edu)",
  "ip_address": "127.0.0.1"
}
```
