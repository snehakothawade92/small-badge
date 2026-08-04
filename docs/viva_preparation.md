# SmallBadge: Digital Badge Issuing & Verification Platform
## Viva Preparation: Common Questions & Answers

This document lists critical technical questions that project examiners, guides, and vivas typically ask, along with simple but professional answers you can give confidently.

---

## 1. Project Overview & Architecture

### Q1: What is the main objective of SmallBadge?
**Answer**: SmallBadge is a secure web application that allows institutions (colleges, companies, bootcamps) to issue tamper-proof digital certificates/badges. These badges can be verified in real-time by employers or the public using a unique Badge Hash ID or by scanning a generated QR code. It eliminates the manual work of verifying paper certificates and prevents credential forgery.

### Q2: Explain the technology stack used in this project.
**Answer**:
* **Frontend**: HTML5, CSS3, JavaScript, and Bootstrap 5 (for responsive layouts).
* **Backend**: Python with the Flask web framework. We use Flask Blueprints to organize modules.
* **Database**: MongoDB (NoSQL) using the PyMongo driver to interface with python dicts.
* **Key Libraries**: `Pillow` and `qrcode` for QR codes, `reportlab` for generating PDF certificates on the fly, and `pandas` for processing student registration spreadsheets (CSVs).

### Q3: Why did you choose Flask over Django?
**Answer**: Flask is a lightweight micro-framework. It allows developers to choose their database (like NoSQL MongoDB) and build components independently. Django is heavy and comes with an ORM pre-tailored for SQL databases. Flask gave us the flexibility to implement custom role-based login logic and NoSQL document schemas without extra overhead.

### Q4: Why did you choose MongoDB over SQL databases (like MySQL)?
**Answer**: Digital badges don't have rigid schema structures. If an organization wants to add custom fields to a badge (e.g., GPA, grade, project link), MongoDB allows us to save variable JSON-like documents without modifying database schemas. Additionally, reading documents by key (Badge ID) is extremely fast in MongoDB, making verification lookups fast.

---

## 2. Authentication & Security (RBAC)

### Q5: What is Role-Based Access Control (RBAC) and how did you build it?
**Answer**: RBAC restricts route access based on a user's role (Super Admin, Org Admin, Student). We implemented it using custom Python decorators (wrappers) in `app/decorators.py`. The decorator intercepts the request, checks `current_user.role`, and returns `403 Forbidden` if the user's role is not authorized for that route.

### Q6: How are passwords secured in the database?
**Answer**: We never save plain text passwords. We hash them using the `bcrypt` library. Bcrypt automatically applies a random "salt" and performs key-stretching (running the hash function thousands of times) to prevent hacking attacks (like brute-force and rainbow table lookups).

---

## 3. Core Features & Algorithms

### Q7: How is a badge uniquely identified and verified?
**Answer**: When an Org Admin issues a badge, we concatenate the student ID, course ID, template ID, and the current timestamp, and run it through the **SHA-256** hash algorithm. This yields a 64-character hexadecimal string called the **Badge ID**.
* This Badge ID forms a public URL: `http://<domain>/verify/<badge_id>`.
* A lookup query runs: `db.issued_badges.find_one({"badge_id": badge_id})`. If found and active, it displays the student, course, and issuer details.

### Q8: How is the QR Code generated?
**Answer**: We use the Python `qrcode` library. We feed it the public verification URL. The library computes the black-and-white grid pattern representing the URL data and outputs a PNG image. We save it to `/static/uploads/qrcodes/<badge_id>.png`.

### Q9: How is the PDF certificate generated dynamically?
**Answer**: We use the `reportlab` library. We create a landscape-oriented `canvas` and programmatically draw borders, text blocks (Student Name, Course Name, Issue Date), and the verification QR code image onto it, saving it directly as a PDF file in `/static/uploads/pdfs/<badge_id>.pdf`.

### Q10: How does the CSV import feature work?
**Answer**: When an Org Admin uploads a `.csv` student list, we read it using the `pandas` library. Pandas parses the file into a DataFrame. We validate that the headers `name`, `email`, and `roll_number` exist, loop through each row, check for duplicates in MongoDB, and insert them into the `students` collection.
