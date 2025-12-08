# Authentication API - Curl Commands

## **1. Register New User**
```bash
curl -X POST http://localhost:8000/api/auth/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { register(input: { email: \"user@example.com\", password: \"password123\", firstName: \"John\", lastName: \"Doe\" }) { success message token user { id username email firstName lastName } } }"
  }'
```

## **2. Login Existing User**
```bash
curl -X POST http://localhost:8000/api/auth/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { login(input: { email: \"user@example.com\", password: \"password123\" }) { success message token user { id username email firstName lastName } } }"
  }'
```

## **3. Get Current User (Protected)**
```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "query": "query { me { id username email firstName lastName isActive dateJoined } }"
  }'
```

## **4. Logout**
```bash
curl -X POST http://localhost:8000/api/auth/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "query": "mutation { logout { success message } }"
  }'
```

## **5. Protected Request - Get Products**
```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -d '{
    "query": "query { products { id sku name category { name } costPrice sellingPrice currentStock } }"
  }'
```

## **6. Test Registration with Existing Email (Should Fail)**
```bash
curl -X POST http://localhost:8000/api/auth/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { register(input: { email: \"user@example.com\", password: \"newpass123\" }) { success message } }"
  }'
```

## **Testing Flow:**

1. **Register a new user** - Use the register curl command
2. **Copy the JWT token** from the response
3. **Replace `YOUR_JWT_TOKEN_HERE`** in protected requests
4. **Test protected endpoints** with the token
5. **Try registering with same email** - Should fail
6. **Login with registered credentials** - Should work

## **Expected Registration Response:**
```json
{
  "data": {
    "register": {
      "success": true,
      "message": "Registration successful",
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "user": {
        "id": "2",
        "username": "user",
        "email": "user@example.com",
        "firstName": "John",
        "lastName": "Doe"
      }
    }
  }
}
```

## **Registration Features:**
- ✅ **Email validation** - Checks for existing users
- ✅ **Auto username** - Generated from email prefix
- ✅ **Unique usernames** - Adds numbers if needed
- ✅ **Immediate login** - Returns JWT token on registration
- ✅ **Optional names** - First/last name are optional
- ✅ **Same response structure** - Consistent with login API