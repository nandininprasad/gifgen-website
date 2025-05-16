# GIFgen

A gif generation pipeline that uses the Wan2.1 model.
Transfomrs natural language, in addition to style choices and optional image generation.


### Installation Guide

To run the front end

```
cd frontend

npm install

npm run dev

```


To run the server

```
cd server

pip install -r requirements.txt

flask run
```

To get the flask server running. 
Configure the HOST ip address in the app.py for the server and the page.txt file in the frontend to match,
so that the frontend and the server can communicate. Please create a file `.env` with your Open AI API key to enable propmpt enhancement.


# Features

- Natural language to Ideal prompt conversion.
- Easy to use style changer.
- Optional Image upload to serve as the starting frame.

