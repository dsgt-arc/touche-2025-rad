#!/usr/bin/env bash

curl -X POST -H "Content-Type: application/json" -d '{
  "messages": [
    {"role":"user","content":"I think that it is always wrong to lie since the ten commandments tell us so."},
    {"role":"assistant","content":"I actually think there is a strong case to be made for the idea that \"There is nothing inherently morally wrong about lying.\" In certain situations, like protecting someones life or preventing harm, lying might be seen as a morally justifiable action."},
    {"role":"user","content":"But \"preventing harm\" is a slippery slope."}
  ]
}' http://localhost:8080
