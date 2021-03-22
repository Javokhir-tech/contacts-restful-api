from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates
import sqlite3

conn = sqlite3.connect('contacts.db')   # connect to db
cur = conn.cursor()


templates = Jinja2Templates(directory='templates')  # using html templates

# get all data
async def list_of_contacts(request):
    contactsDB = cur.execute("SELECT * FROM contacts WHERE name IS NOT NULL")

    return templates.TemplateResponse('index.html', {'request':    request, 'contacts': [person for person in contactsDB]})

# post method, gets data from template
async def create_contact(request):

    inp = await request.form()  # get value from form
    name = inp.get("name")
    phone = inp.get("phone")
    cur.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))  # insert into db
    conn.commit()

    return templates.TemplateResponse('postcontact.html', {'request':    request})

# get 1 contact e.g GET/ http://127.0.0.1:8000/contacts/7
async def get_contact(request):
    user_id = request.path_params['id']
    person = cur.execute("SELECT * FROM contacts WHERE id = :user_id", {"user_id":user_id})
    
    return templates.TemplateResponse('getcontact.html', {'request':    request, 'person': [c for c in person]})

# delete method
async def delete_contact(request):
    user_id = request.path_params['id']
    person = cur.execute(
        "DELETE FROM contacts WHERE id = :user_id", {"user_id": user_id})
    conn.commit()
    return JSONResponse({f"Contact {user_id}": "deleted"})

# put method
async def update_contact(request):
    user_id = request.path_params['id']
    
    data = await request.json() # get body data from postman
    personUpdated = cur.execute(
        """UPDATE contacts SET name=?, phone=? WHERE id = ?""", (data["name"], data["phone"], user_id))
    conn.commit()
    return JSONResponse({f"Contact {user_id}": "updated"})  # {"name":"Johhnyy","phone":"1111111"}

# routing
routes = [
    Route('/contacts', list_of_contacts),
    Route('/contacts', create_contact, methods=['POST']),
    Route('/contacts/{id:int}', get_contact, methods=['GET']),
    Route('/contacts/{id:int}', delete_contact, methods=['DELETE']),
    Route('/contacts/{id:int}', update_contact, methods=['PUT']),
]
app = Starlette(debug=True, routes=routes)
"""
    contacts table in contacts.db
    CREATE TABLE IF NOT EXISTS "contacts" (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
    name TEXT,
    phone INTEGER
    );
"""
