from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Backend import models,settings,engine,router_person,router_auth,router_Events

app=FastAPI()
origins=[
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(engine)
# print(set(settings))
app.include_router(router_person)
app.include_router(router_auth)
app.include_router(router_Events)