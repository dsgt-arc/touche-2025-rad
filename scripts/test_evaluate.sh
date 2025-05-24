#!/usr/bin/env bash

curl -X POST -H "Content-Type: application/json" -d '{
    "simulation": {
      "configuration": {
        "topic": {
          "description": "Does pineapple belong on pizza?"
        },
        "user": {
          "class": "Touche25RADUser",
          "url": "https://touche25-rad.webis.de/user-sim/api/chat",
          "model": "base-user"
        },
        "system": {
          "class": "BasicChatSystem",
          "url": "http://localhost:8080"
        },
        "maxTurns": 1
      },
      "userTurns": [
        {
          "utterance": "Personally, I think pineapple can be a palatable addition to pizza in Hawaiian or sweet-and-savory pair combinations but does not universally deserve to accompany tomato sauce and various meats.",
          "systemResponse": {
            "utterance": "Pineapple sweetness and sourness offer a valid taste balance on pizza, contrasting salty elements like cheese. Its inclusion enhances the overall flavor profile, a balance chefs often seek in a dish, rather than being universally unsuitable.",
            "response": {
              "arguments": [
                {
                  "id": "10104.1153",
                  "text": "Pineapple can work against other juicy, sweet fruit toppings (like watermelon and cherries) on a savory pizza."
                }
              ]
            }
          }
        }
      ],
      "milliseconds": 5306.9081279999955
    },
    "userTurnIndex": null
}' http://localhost:8080/quality
