


## **API Documentation v1.0**

### **Authentication & User Management**

#### **1. POST /api/1.0/auth/register**
**Creates a new user account**

**Request Body:**
```json
{
    "first_name": "string (required)",
    "second_name": "string (optional)",
    "email": "string (required, unique)",
    "phone": "string (optional)",
    "password": "string (required, min 8 chars)"
}
```

**Response:**
```json
{
    "msg": "Registration successful",
    "user": {
        "id": "int",
        "first_name": "string",
        "second_name": "string|null",
        "email": "string",
        "phone": "string|null"
    }
}
```

**Errors:**
- `DuplicateEmailError` (400) - When email already exists

---

#### **2. POST /api/1.0/auth/login**
**Authenticates a user**

**Request Body:**
```json
{
    "email": "string (required)",
    "password": "string (required)"
}
```

**Response:**
```json
{
    "token": "string (JWT)",
    "msg": "Login successful"
}
```

**Errors:**
- `AuthenticationError` (401) - Invalid credentials

---

### **Token Management**

#### **3. POST /api/1.0/auth/token**
**Generates a new access token**

**Request Headers:**
```
Authorization: Bearer <master_token>
```

**Request Body:**
```json
{
    "level": "string (read|write|read_write)",
    "description": "string (optional)"
}
```

**Response:**
```json
{
    "token": "string (new JWT)"
}
```

---

#### **4. DELETE /api/1.0/auth/token**
**Revokes tokens**

**Option 1 (Revoke master token):**
```json
{
    "email": "string",
    "password": "string"
}
```

**Option 2 (Revoke child token):**
```json
{
    "master_token": "string",
    "child_token": "string"
}
```

**Response:**
```json
{
    "success": true
}
```

---

### **Education Records**

#### **5. POST /api/1.0/user/education**
**Adds education record**

**Request Body:**
```json
{
    "entity_level": "int (1-5, required)",
    "entity_name": "string (required)",
    "certification": "string (optional)"
}
```

**Response:**
```json
{
    "msg": "Education record added.",
    "id": "int",
    "entity_level": "int",
    "entity_name": "string",
    "certification": "string|null"
}
```

---

#### **6. GET /api/1.0/user/education**
**Retrieves education records**

**Query Params:**
- `id` (optional) - Filter by specific record

**Response:**
```json
[
    {
        "id": "int",
        "entity_level": "int",
        "entity_name": "string",
        "certification": "string|null"
    }
]
```

---

#### **7. PUT /api/1.0/user/education**
**Updates education record**

**Request Body:**
```json
{
    "id": "int (required)",
    "entity_level": "int (optional)",
    "entity_name": "string (optional)",
    "certification": "string (optional)"
}
```

**Response:**
```json
{
    "msg": "Education record updated."
}
```

---

#### **8. DELETE /api/1.0/user/education**
**Deletes education record**

**Request Body:**
```json
{
    "id": "int (required)"
}
```

**Response:**
```json
{
    "msg": "Education record deleted."
}
```

---

### **Work Experience**

#### **9. POST /api/1.0/user/work**
**Adds work experience**

**Request Body:**
```json
{
    "organization_name": "string (required)",
    "description": "string (required)",
    "witness": "string (required)",
    "comment": "string (optional)"
}
```

**Response:**
```json
{
    "msg": "Work experience added.",
    "id": "int",
    "organization_name": "string",
    "description": "string",
    "witness": "string",
    "comment": "string|null"
}
```

---

#### **10. GET /api/1.0/user/work**
**Retrieves work experiences**

**Query Params:**
- `id` (optional) - Filter by specific record

**Response:**
```json
[
    {
        "id": "int",
        "organization_name": "string",
        "description": "string",
        "witness": "string",
        "comment": "string|null"
    }
]
```

---

#### **11. PUT /api/1.0/user/work**
**Updates work record**

**Request Body:**
```json
{
    "id": "int (required)",
    "organization_name": "string (optional)",
    "description": "string (optional)",
    "witness": "string (optional)",
    "comment": "string (optional)"
}
```

**Response:**
```json
{
    "msg": "Work record updated."
}
```

---

#### **12. DELETE /api/1.0/user/work**
**Deletes work record**

**Request Body:**
```json
{
    "id": "int (required)"
}
```

**Response:**
```json
{
    "msg": "Work record deleted."
}
```

---

### **Optional Content (Skills/Awards/Projects)**

#### **13. POST /api/1.0/user/optional**
**Adds optional record**

**Request Body:**
```json
{
    "type": "string (skill|award|project, required)",
    "title": "string (required)",
    "description": "string (required)",
    "date": "string (YYYY-MM-DD)"
}
```

**Response:**
```json
{
    "msg": "Record added.",
    "id": "int",
    "type": "string",
    "title": "string",
    "description": "string",
    "date": "string"
}
```

---

#### **14. GET /api/1.0/user/optional**
**Retrieves optional records**

**Query Params:**
- `id` (optional) - Filter by specific record
- `type` (optional) - Filter by type

**Response:**
```json
[
    {
        "id": "int",
        "type": "string",
        "title": "string",
        "description": "string",
        "date": "string"
    }
]
```

---

#### **15. PUT /api/1.0/user/optional**
**Updates optional record**

**Request Body:**
```json
{
    "id": "int (required)",
    "type": "string (optional)",
    "title": "string (optional)",
    "description": "string (optional)",
    "date": "string (optional)"
}
```

**Response:**
```json
{
    "msg": "Record updated."
}
```

---

#### **16. DELETE /api/1.0/user/optional**
**Deletes optional record**

**Request Body:**
```json
{
    "id": "int (required)"
}
```

**Response:**
```json
{
    "msg": "Record deleted."
}
```

---

### **User Profile**

#### **17. GET /api/1.0/user/profile**
**Gets user profile**

**Response:**
```json
{
    "id": "int",
    "first_name": "string",
    "second_name": "string|null",
    "email": "string",
    "phone": "string|null"
}
```

---

**Notes:**
1. All endpoints except `/auth/register` and `/auth/login` require authentication
2. Token must be included in headers: `Authorization: Bearer <token>`
3. Timestamps are in ISO 8601 format
4. Error responses follow format: `{"msg": "...", "type": "...", "description": "..."}`