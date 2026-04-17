from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS (opcional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo Pydantic para un contacto
class Contact(BaseModel):
    id: int
    name: str
    phone: str
    email: str

# Almacenamiento en memoria
contacts = []
next_id = 1

@app.post("/contacts/", response_model=Contact)
def create_contact(contact: Contact):
    """Crear un nuevo contacto."""
    global next_id
    contact.id = next_id
    contacts.append(contact)
    next_id += 1
    return contact

@app.get("/contacts/", response_model=List[Contact])
def list_contacts():
    """Listar todos los contactos."""
    return contacts

@app.get("/contacts/{contact_id}", response_model=Contact)
def get_contact(contact_id: int):
    """Obtener un contacto por ID."""
    for contact in contacts:
        if contact.id == contact_id:
            return contact
    raise HTTPException(status_code=404, detail="Contact not found")

@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, updated_contact: Contact):
    """Actualizar un contacto existente."""
    for index, contact in enumerate(contacts):
        if contact.id == contact_id:
            contacts[index] = updated_contact
            contacts[index].id = contact_id  # Mantener el ID original
            return contacts[index]
    raise HTTPException(status_code=404, detail="Contact not found")

@app.delete("/contacts/{contact_id}", response_model=Contact)
def delete_contact(contact_id: int):
    """Eliminar un contacto por ID."""
    for index, contact in enumerate(contacts):
        if contact.id == contact_id:
            return contacts.pop(index)
    raise HTTPException(status_code=404, detail="Contact not found")

# Para ejecutar: uvicorn main:app --reload