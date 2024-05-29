with open('./app/description.md', encoding='utf-8') as file:
    description = file.read()

application_metadata = {
    "title": "API",
    "description": description,
    "version": "0.0.1.dev1",
}
