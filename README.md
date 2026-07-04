# MyPostman-2026
This contains my personal postman project. I am building with python.

Here is a complete, purely flat numbered list detailing every specific action and capability your Lightweight API Tester (Pro Edition) can perform:

1. **Send standard HTTP requests:** Choose between GET, POST, PUT, DELETE, and PATCH methods using a dropdown menu.
2. **Target any endpoint:** Type or paste any valid web URL or local IP address into the address bar to send traffic to it.
3. **Send JSON payloads:** Type or paste raw text/JSON into the dedicated "JSON Body" tab to send data alongside POST, PUT, or PATCH requests.
4. **Auto-inject content headers:** Automatically sends a `Content-Type: application/json` header if you include body data but forget to define the header yourself.
5. **Add custom headers:** Use a dynamic table to add unlimited Key/Value pairs for HTTP headers (e.g., `Authorization`, `Accept`, `User-Agent`).
6. **Add query parameters:** Use a dynamic table to visually build URL query strings (e.g., `?limit=10&sort=desc`) without manually typing them into the URL bar.
7. **Filter empty data:** Automatically ignores empty rows in your Header and Parameter tables so blank data is never sent to the server.
8. **View status codes:** Displays the exact HTTP status code and text response (e.g., `200 OK`, `500 Internal Server Error`) prominently above the response output.
9. **Pretty-print JSON responses:** Automatically detects if a server responds with JSON and formats it with proper indentation and line breaks for readability.
10. **Read raw text/HTML:** Gracefully defaults to displaying the raw text or HTML string if the server does not return valid JSON data.
11. **Catch connection errors:** Intercepts failed connections (like offline networks or invalid URLs) and displays a clean error message in the UI instead of crashing the app.
12. **Manage multiple tabs:** Open, view, and close multiple independent API requests at the exact same time using the top tab bar.
13. **Save request states:** Save the exact configuration of your current tab (Method, URL, Headers, Params, and Body) by giving it a custom name.
14. **View saved collections:** Browse a persistent, clickable sidebar list of all the requests you have previously saved.
15. **Load requests safely:** Click any saved item in the sidebar to instantly load its exact configuration into a *brand-new* tab, protecting your current work.
16. **Delete saved requests:** Remove outdated or incorrect requests from your sidebar collection (includes a safety confirmation prompt).
17. **Persist collection data locally:** Automatically writes your saved requests to a `postman_collections.json` file on your hard drive so they survive app restarts.
18. **Manage environments via JSON:** Open a dedicated dialog box to write and save multiple testing environments (e.g., "Development", "Production") using standard JSON syntax.
19. **Switch active environments:** Use a top-level dropdown menu to instantly swap which environment (and its associated variables) is currently active.
20. **Highlight active environments:** Visually changes the color of the environment dropdown to remind you when you are not using the default "Global" setup.
21. **Auto-swap dynamic variables:** Automatically finds any text wrapped in double brackets (like `{{base_url}}` or `{{api_key}}`) in your UI and replaces it with the real data from your active environment just milliseconds before the request is sent.
22. **Persist environment data locally:** Automatically writes your environment configurations to a `postman_envs.json` file on your hard drive to keep your API keys and URLs permanently saved.
23. Jwt decoder 
