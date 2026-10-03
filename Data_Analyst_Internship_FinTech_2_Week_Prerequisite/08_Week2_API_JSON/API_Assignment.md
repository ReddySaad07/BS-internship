# REST API & JSON Assignment

## API used
JSONPlaceholder public REST API.

## Endpoint
`https://jsonplaceholder.typicode.com/posts?userId=1`

## Method
GET

## Process
1. Send a GET request.
2. Read the JSON response.
3. Validate that the response is a non-empty list.
4. Convert JSON records to CSV using Python.
5. Save the result as `api_posts.csv`.

## Authentication
This demonstration endpoint does not require credentials.

## Limitations
This is a practice/public test API. It is not financial or production data.

## Run
```bash
python extract_api_to_csv.py
```
